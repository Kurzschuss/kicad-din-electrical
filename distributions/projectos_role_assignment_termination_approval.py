"""Freigabegesteuerte Wirksamkeit administrativer Rollenzuweisungs-Beendigungen."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_project_roles import ProjectOSUserProjectRole

_ALLOWED_RISKS = {"low", "medium", "high", "critical"}
_TARGET_PREFIX = "role_assignment_termination:"


class ProjectOSApprovedRoleAssignmentTerminationEvaluator:
    """Bewertet Rollenzuweisungs-Beendigungen ohne Domainmutation read-only."""

    def __init__(
        self,
        *,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        risk_class_map: Mapping[str, str] | None = None,
    ) -> None:
        self.roles = tuple(roles or ())
        self.terminations = tuple(terminations or ())
        self.approval_requests = tuple(approval_requests or ())
        self.approvals = tuple(approvals or ())
        self.risk_class_map = {
            str(role_type).strip(): str(risk).strip().lower()
            for role_type, risk in (risk_class_map or {}).items()
            if str(role_type).strip()
        }
        invalid = {risk for risk in self.risk_class_map.values() if risk not in _ALLOWED_RISKS}
        if invalid:
            raise ValueError(f"unsupported risk_class: {sorted(invalid)[0]}")

        role_ids = {item.role_assignment_id for item in self.roles}
        termination_ids = {item.termination_id for item in self.terminations}
        for termination in self.terminations:
            if termination.role_assignment_id not in role_ids:
                raise ValueError("role assignment termination references unknown role_assignment_id")

        seen_targets: set[str] = set()
        for request in self.approval_requests:
            if request.action_type != "role_assignment_termination":
                continue
            termination_id = self._target_id(request.target_reference)
            if termination_id not in termination_ids:
                raise ValueError("approval request references unknown role assignment termination")
            if termination_id in seen_targets:
                raise ValueError("multiple approval requests for role assignment termination")
            seen_targets.add(termination_id)

    @staticmethod
    def target_reference(termination_id: str) -> str:
        return f"{_TARGET_PREFIX}{termination_id}"

    @staticmethod
    def _target_id(target_reference: str) -> str:
        value = str(target_reference)
        if not value.startswith(_TARGET_PREFIX):
            raise ValueError("role assignment termination approval target_reference must use role_assignment_termination:<id>")
        termination_id = value[len(_TARGET_PREFIX):]
        if not termination_id:
            raise ValueError("role assignment termination approval target is empty")
        return termination_id

    def _role(self, termination: ProjectOSProjectRoleAssignmentTermination) -> ProjectOSUserProjectRole:
        matches = [item for item in self.roles if item.role_assignment_id == termination.role_assignment_id]
        if len(matches) != 1:
            raise ValueError("role assignment termination role is ambiguous")
        return matches[0]

    def _request(self, termination: ProjectOSProjectRoleAssignmentTermination) -> ProjectOSRoleActionApprovalRequest | None:
        target = self.target_reference(termination.termination_id)
        matches = [
            item for item in self.approval_requests
            if item.action_type == "role_assignment_termination"
            and item.target_reference == target
        ]
        if len(matches) > 1:
            raise ValueError("multiple approval requests for role assignment termination")
        return matches[0] if matches else None

    def _approval_state(
        self,
        termination: ProjectOSProjectRoleAssignmentTermination,
        role: ProjectOSUserProjectRole,
    ) -> tuple[str, dict[str, Any]]:
        risk_class = self.risk_class_map.get(role.role_type, "low")
        request = self._request(termination)
        if request is None:
            if risk_class in {"high", "critical"}:
                return risk_class, {
                    "status": "approval_missing",
                    "effective": False,
                    "approval_required": True,
                    "second_person_required": True,
                    "post_review_required": False,
                    "request": None,
                    "read_only": True,
                }
            return risk_class, {
                "status": "approved_not_required",
                "effective": True,
                "approval_required": False,
                "second_person_required": False,
                "post_review_required": False,
                "request": None,
                "read_only": True,
            }
        if request.project_id != termination.project_id:
            raise ValueError("role assignment termination approval belongs to another project")
        if request.scope != termination.scope:
            raise ValueError("role assignment termination approval scope does not match termination")
        if request.risk_class != risk_class:
            raise ValueError("role assignment termination approval risk_class does not match role risk")
        return risk_class, ProjectOSRoleActionApprovalEvaluator(self.approvals).evaluate(request)

    def state(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("role assignment termination evaluation time must include timezone")
        current = current.astimezone(timezone.utc)

        effective: list[ProjectOSProjectRoleAssignmentTermination] = []
        blocked: list[dict[str, Any]] = []
        scheduled: list[dict[str, Any]] = []
        pending_reviews: list[dict[str, Any]] = []
        states: list[dict[str, Any]] = []

        for termination in self.terminations:
            if termination.project_id != project_id or termination.user_id != user.user_id or termination.scope != scope:
                continue
            role = self._role(termination)
            risk_class, approval = self._approval_state(termination, role)
            row = {
                "termination": termination.as_dict(),
                "role": role.as_dict(),
                "risk_class": risk_class,
                "approval": approval,
            }
            states.append(row)
            if not termination.is_effective(current):
                scheduled.append(row)
                continue
            if approval["effective"]:
                effective.append(termination)
                if approval.get("post_review_required"):
                    pending_reviews.append(row)
            else:
                blocked.append(row)

        return {
            "project_id": project_id,
            "user": user.as_dict(),
            "scope": scope,
            "evaluated_at": current.isoformat(),
            "termination_states": states,
            "effective_terminations": [item.as_dict() for item in effective],
            "blocked_terminations": blocked,
            "scheduled_terminations": scheduled,
            "pending_post_reviews": pending_reviews,
            "read_only": True,
        }

    def effective_terminations(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
    ) -> tuple[ProjectOSProjectRoleAssignmentTermination, ...]:
        state = self.state(project_id=project_id, user=user, scope=scope, at=at)
        ids = {item["termination_id"] for item in state["effective_terminations"]}
        return tuple(item for item in self.terminations if item.termination_id in ids)
