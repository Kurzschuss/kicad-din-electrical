"""Simulation-First Kompensationsplan für ProjectOS-Rollenzuweisungen.

Der Planner mutiert keinen Fachzustand. Er bewertet vorab Autorisierung, konfigurierte
Risikoklasse, Vier-Augen-/Nachprüfungsstatus und den erwarteten Verlust rollenabgeleiteter
Rechte. Generisches mutierendes Rollen-Undo bleibt davon ausdrücklich getrennt.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_role_assignment_termination_approval import (
    ProjectOSApprovedRoleAssignmentTerminationEvaluator,
)
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReviewEvaluator
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext


class ProjectOSRoleCompensationPlanner:
    """Erstellt einen rein lesenden Plan für die Kompensation einer Rollenzuweisung."""

    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.manager = runtime.manager
        self.policy = runtime.policy

    @staticmethod
    def _time(at: datetime | None) -> datetime:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("role compensation planning time must include timezone")
        return current.astimezone(timezone.utc)

    def _role(self, role_assignment_id: str):
        matches = [
            item for item in self.manager.user_management.project_roles
            if item.role_assignment_id == role_assignment_id
        ]
        if len(matches) != 1:
            raise ValueError("role compensation target is unknown or ambiguous")
        return matches[0]

    def _user(self, user_id: str):
        matches = [item for item in self.manager.user_management.users if item.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("role compensation user is unknown or ambiguous")
        return matches[0]

    def _authorization(self, actor_user_id: str, current: datetime) -> dict[str, Any]:
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor_user_id,
            correlation_id=str(uuid4()),
        )
        return self.runtime.authorization.evaluate(
            "project_role_assignment_terminated",
            context,
            at=current,
        )

    def _termination_row(self, role, user, current: datetime) -> tuple[Any | None, dict[str, Any] | None]:
        state = self.manager.user_management
        matches = [
            item for item in state.role_assignment_terminations
            if item.role_assignment_id == role.role_assignment_id
        ]
        if len(matches) > 1:
            raise ValueError("multiple role assignment terminations are ambiguous")
        if not matches:
            return None, None
        termination = matches[0]
        evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
            roles=state.project_roles,
            terminations=state.role_assignment_terminations,
            approval_requests=state.approval_requests,
            approvals=state.approvals,
            risk_class_map=self.policy.role_risk_class_map,
        )
        evaluated = evaluator.state(
            project_id=state.project_id,
            user=user,
            scope=role.scope,
            at=current,
        )
        rows = [
            item for item in evaluated["termination_states"]
            if item["termination"]["termination_id"] == termination.termination_id
        ]
        if len(rows) != 1:
            raise ValueError("role assignment termination evaluation is ambiguous")
        return termination, rows[0]

    def _post_review(self, termination_row: dict[str, Any] | None) -> dict[str, Any] | None:
        if termination_row is None:
            return None
        approval = termination_row["approval"]
        request_data = approval.get("request")
        if request_data is None:
            return None
        action_id = request_data.get("action_id")
        request = next(
            (item for item in self.manager.user_management.approval_requests if item.action_id == action_id),
            None,
        )
        if request is None or not request.emergency:
            return None
        return ProjectOSRoleEmergencyPostReviewEvaluator(
            approvals=self.manager.user_management.approvals,
            reviews=self.manager.user_management.post_reviews,
        ).evaluate(request)

    def _permissions_at_risk(self, role, user, current: datetime, risk_class: str | None) -> tuple[list[str], bool]:
        if risk_class is None:
            return [], False
        state = self.manager.user_management
        target_termination_ids = {
            item.termination_id
            for item in state.role_assignment_terminations
            if item.role_assignment_id == role.role_assignment_id
        }
        other_terminations = tuple(
            item for item in state.role_assignment_terminations
            if item.termination_id not in target_termination_ids
        )
        target_references = {
            ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(item)
            for item in target_termination_ids
        }
        requests = tuple(
            item for item in state.approval_requests
            if not (
                item.action_type == "role_assignment_termination"
                and item.target_reference in target_references
            )
        )
        evaluator = ProjectOSApprovedRoleActivationEvaluator(
            roles=state.project_roles,
            activations=state.activations,
            role_terminations=other_terminations,
            approval_requests=requests,
            approvals=state.approvals,
            risk_class_map=self.policy.role_risk_class_map,
        )
        assignments = evaluator.permission_assignments(
            project_id=state.project_id,
            user=user,
            permission_map=self.policy.role_permission_map,
            scope=role.scope,
            at=current,
        )
        permissions = sorted({
            item.permission for item in assignments
            if item.metadata.get("role_assignment_id") == role.role_assignment_id
        })
        return permissions, True

    @staticmethod
    def _next_action(
        *,
        actor_authorized: bool,
        risk_class: str | None,
        termination_present: bool,
        approval_status: str | None,
        termination_effective: bool,
        post_review_required: bool,
    ) -> str:
        if not actor_authorized:
            return "obtain_role_terminate_permission"
        if risk_class is None:
            return "configure_role_risk"
        if not termination_present:
            if risk_class in {"high", "critical"}:
                return "create_termination_then_request_approval"
            return "execute_termination"
        if termination_effective and post_review_required:
            return "complete_post_review"
        if termination_effective:
            return "reassignment_possible"
        if approval_status in {"approval_missing", "pending_approval"}:
            return "request_or_wait_for_approval"
        if approval_status == "rejected":
            return "resolve_rejected_termination"
        if approval_status == "risk_not_configured":
            return "configure_role_risk"
        return "wait_until_termination_effective"

    def plan(
        self,
        *,
        role_assignment_id: str,
        actor_user_id: str,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = self._time(at)
        role = self._role(role_assignment_id)
        user = self._user(role.user_id)
        authorization = self._authorization(actor_user_id, current)
        actor_authorized = bool(authorization.get("allowed", False))
        risk_class = self.policy.role_risk_class_map.get(role.role_type)
        termination, termination_row = self._termination_row(role, user, current)
        approval = termination_row["approval"] if termination_row is not None else None
        approval_status = approval.get("status") if approval is not None else None
        termination_effective = bool(
            termination is not None
            and termination.is_effective(current)
            and approval is not None
            and approval.get("effective", False)
        )
        post_review = self._post_review(termination_row)
        post_review_required = bool(
            post_review["post_review_required"] if post_review is not None
            else approval.get("post_review_required", False) if approval is not None
            else False
        )
        permissions, impact_complete = self._permissions_at_risk(role, user, current, risk_class)
        second_person_required = risk_class in {"high", "critical"}
        configuration_required = risk_class is None
        compensation_completed = bool(termination_effective and not post_review_required)
        synchronous_possible = bool(
            actor_authorized
            and not configuration_required
            and termination is None
            and not second_person_required
        )
        requires_multistep = bool(
            second_person_required
            or post_review_required
            or (
                termination is not None
                and approval_status in {"approval_missing", "pending_approval", "rejected", "risk_not_configured"}
            )
        )
        next_action = self._next_action(
            actor_authorized=actor_authorized,
            risk_class=risk_class,
            termination_present=termination is not None,
            approval_status=approval_status,
            termination_effective=termination_effective,
            post_review_required=post_review_required,
        )
        return {
            "project_id": self.manager.user_management.project_id,
            "role_assignment": role.as_dict(),
            "actor_user_id": actor_user_id,
            "scope": role.scope,
            "evaluated_at": current.isoformat(),
            "authorization": authorization,
            "actor_authorized": actor_authorized,
            "required_permission": authorization.get("required_permission"),
            "risk_class": risk_class,
            "configuration_required": configuration_required,
            "second_person_required": second_person_required,
            "termination_present": termination is not None,
            "termination": termination.as_dict() if termination is not None else None,
            "termination_approval_status": approval_status,
            "termination_effective": termination_effective,
            "post_review": post_review,
            "post_review_required": post_review_required,
            "compensation_completed": compensation_completed,
            "synchronous_compensation_possible": synchronous_possible,
            "requires_multistep_lifecycle": requires_multistep,
            "effective_role_permissions_at_risk": permissions,
            "permission_impact_assessment_complete": impact_complete,
            "reassignment_possible_now": termination_effective,
            "reassignment_creates_new_role_assignment_id": True,
            "next_action": next_action,
            "generic_role_undo_enabled": False,
            "domain_mutation": False,
            "audit_mutation": False,
            "bus_mutation": False,
            "read_only": True,
            "persisted": False,
        }
