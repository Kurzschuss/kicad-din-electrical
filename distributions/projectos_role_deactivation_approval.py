"""Freigabegesteuerte Wirksamkeit von Projektfunktions-Beendigungen.

Kritische Beendigungen wirken fail-closed: Ohne passenden Freigabeauftrag und
wirksame Vier-Augen-Entscheidung bleibt die zugrunde liegende Aktivierung wirksam.
Notfall-Beendigungen dürfen vorläufig wirken, bleiben aber nachprüfungspflichtig.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_role_deactivation import (
    ProjectOSProjectRoleDeactivation,
    ProjectOSProjectRoleLifecycleEvaluator,
)
from .projectos_user_project_roles import ProjectOSUserProjectRole


class ProjectOSApprovedRoleDeactivationEvaluator:
    """Bewertet Rollenrückgaben unter Berücksichtigung des Freigabestatus."""

    def __init__(
        self,
        *,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        deactivations: Iterable[ProjectOSProjectRoleDeactivation] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
    ) -> None:
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.deactivations = tuple(deactivations or ())
        self.approval_requests = tuple(approval_requests or ())
        self.approvals = tuple(approvals or ())

        deactivation_ids = {item.deactivation_id for item in self.deactivations}
        seen_targets: set[str] = set()
        for request in self.approval_requests:
            if request.action_type != "deactivation":
                continue
            target = self._target_id(request.target_reference)
            if target not in deactivation_ids:
                raise ValueError("approval request references unknown deactivation_id")
            if target in seen_targets:
                raise ValueError("multiple approval requests for deactivation_id")
            seen_targets.add(target)

    @staticmethod
    def _target_id(target_reference: str) -> str:
        prefix = "deactivation:"
        if not str(target_reference).startswith(prefix):
            raise ValueError("deactivation approval target_reference must use deactivation:<id>")
        return str(target_reference)[len(prefix):]

    def _approval_state(self, deactivation: ProjectOSProjectRoleDeactivation, risk_class: str) -> dict[str, Any]:
        matching = [
            request for request in self.approval_requests
            if request.action_type == "deactivation"
            and self._target_id(request.target_reference) == deactivation.deactivation_id
        ]
        if not matching:
            if risk_class in {"high", "critical"}:
                return {
                    "status": "approval_missing",
                    "effective": False,
                    "post_review_required": False,
                    "request": None,
                    "read_only": True,
                }
            return {
                "status": "approved_not_required",
                "effective": True,
                "post_review_required": False,
                "request": None,
                "read_only": True,
            }
        request = matching[0]
        if request.risk_class != risk_class:
            raise ValueError("deactivation risk_class does not match approval request")
        return ProjectOSRoleActionApprovalEvaluator(self.approvals).evaluate(request)

    def state(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
        risk_class: str = "low",
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("deactivation approval evaluation time must include timezone")

        effective_deactivations = []
        blocked_deactivations = []
        pending_post_reviews = []
        approval_states = []
        for item in self.deactivations:
            if item.project_id != project_id or item.user_id != user.user_id or item.scope != scope:
                continue
            approval = self._approval_state(item, risk_class)
            approval_states.append({"deactivation": item.as_dict(), "approval": approval})
            if approval["effective"]:
                effective_deactivations.append(item)
                if approval.get("post_review_required"):
                    pending_post_reviews.append(item.deactivation_id)
            else:
                blocked_deactivations.append({"deactivation": item.as_dict(), "approval": approval})

        lifecycle = ProjectOSProjectRoleLifecycleEvaluator(
            roles=self.roles,
            activations=self.activations,
            deactivations=effective_deactivations,
        )
        state = lifecycle.state(project_id=project_id, user=user, scope=scope, at=current)
        state.update({
            "approval_states": approval_states,
            "blocked_deactivations": blocked_deactivations,
            "pending_post_reviews": pending_post_reviews,
            "risk_class": risk_class,
            "read_only": True,
        })
        return state

    def permission_assignments(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        permission_map: dict[str, Iterable[str]],
        scope: str = "project",
        at: datetime | None = None,
        risk_class: str = "low",
    ) -> tuple[ProjectOSPermissionAssignment, ...]:
        current = at or datetime.now(timezone.utc)
        state = self.state(project_id=project_id, user=user, scope=scope, at=current, risk_class=risk_class)
        effective_deactivation_ids = {
            item["deactivation"]["deactivation_id"]
            for item in state["approval_states"]
            if item["approval"]["effective"]
        }
        effective_deactivations = [
            item for item in self.deactivations if item.deactivation_id in effective_deactivation_ids
        ]
        return ProjectOSProjectRoleLifecycleEvaluator(
            roles=self.roles,
            activations=self.activations,
            deactivations=effective_deactivations,
        ).permission_assignments(
            project_id=project_id,
            user=user,
            permission_map=permission_map,
            scope=scope,
            at=current,
            risk_class=risk_class,
        )
