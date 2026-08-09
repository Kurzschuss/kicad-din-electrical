"""Read-only Z_Cockpit-Sicht für freigabegesteuerte Projektfunktionsaktivierung."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_deactivation import ProjectOSUserDeactivation
from .projectos_user_reactivation import ProjectOSUserReactivation
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_authorization import ZCockpitAuthorizationView

_STATUS_LABELS = {
    "risk_not_configured": "Risikoklasse nicht konfiguriert",
    "approval_missing": "Freigabeauftrag fehlt",
    "pending_approval": "Freigabe ausstehend",
    "approved": "Freigegeben",
    "approved_not_required": "Keine zweite Freigabe erforderlich",
    "rejected": "Abgelehnt",
    "emergency_pending_review": "Notfall vorläufig wirksam – Nachprüfung erforderlich",
}


class ZCockpitApprovedRoleActivationView:
    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        role_terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
        risk_class_map: dict[str, str] | None = None,
        user_deactivations: Iterable[ProjectOSUserDeactivation] | None = None,
        user_reactivations: Iterable[ProjectOSUserReactivation] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.base_assignments = tuple(base_assignments or ())
        self.user_deactivations = tuple(user_deactivations or ())
        self.user_reactivations = tuple(user_reactivations or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}
        self.evaluator = ProjectOSApprovedRoleActivationEvaluator(
            roles=roles,
            activations=activations,
            role_terminations=role_terminations,
            approval_requests=approval_requests,
            approvals=approvals,
            risk_class_map=risk_class_map,
            user_deactivations=self.user_deactivations,
            user_reactivations=self.user_reactivations,
        )

    @staticmethod
    def _decorate_approval(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["approval"] = dict(result["approval"])
        status = result["approval"].get("status")
        result["approval"]["status_label"] = _STATUS_LABELS.get(status, str(status))
        return result

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        approval_state = self.evaluator.state(project_id=self.project_id, user=self.user, scope=scope, at=at)
        derived = self.evaluator.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        auth = ZCockpitAuthorizationView(
            self.user,
            self.base_assignments + derived,
            user_deactivations=self.user_deactivations,
            user_reactivations=self.user_reactivations,
        )
        permissions = sorted({
            item.permission
            for item in self.base_assignments + derived
            if item.user_id == self.user.user_id and item.scope == scope
        })
        rights = [auth.state(permission, scope=scope, at=at) for permission in permissions]
        termination_state = approval_state["role_assignment_termination_approvals"]
        termination_approvals = {
            "termination_states": [self._decorate_approval(item) for item in termination_state["termination_states"]],
            "effective_terminations": list(termination_state["effective_terminations"]),
            "blocked_terminations": [self._decorate_approval(item) for item in termination_state["blocked_terminations"]],
            "scheduled_terminations": [self._decorate_approval(item) for item in termination_state["scheduled_terminations"]],
            "pending_post_reviews": [self._decorate_approval(item) for item in termination_state["pending_post_reviews"]],
            "configuration_required": bool(termination_state.get("configuration_required")),
            "read_only": True,
        }
        blocked_activations = [self._decorate_approval(item) for item in approval_state["blocked_activations"]]
        pending_reviews = [self._decorate_approval(item) for item in approval_state["pending_post_reviews"]]
        return {
            "project_id": approval_state["project_id"],
            "user": self.user.as_dict(),
            "scope": scope,
            "effective_activations": [self._decorate_approval(item) for item in approval_state["effective_activations"]],
            "blocked_activations": blocked_activations,
            "pending_post_reviews": pending_reviews,
            "terminated_assigned_roles": list(approval_state["terminated_assigned_roles"]),
            "role_assignment_termination_approvals": termination_approvals,
            "rights": rights,
            "user_lifecycle_status": approval_state.get("user_lifecycle_status", "active"),
            "user_deactivated": bool(approval_state.get("user_deactivated")),
            "user_deactivation": approval_state.get("user_deactivation"),
            "user_reactivation": approval_state.get("user_reactivation"),
            "post_review_required": bool(pending_reviews or termination_approvals["pending_post_reviews"]),
            "attention_required": bool(
                blocked_activations
                or pending_reviews
                or termination_approvals["blocked_terminations"]
                or termination_approvals["pending_post_reviews"]
                or termination_approvals["configuration_required"]
            ),
            "read_only": True,
        }
