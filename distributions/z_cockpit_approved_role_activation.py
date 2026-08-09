"""Read-only Z_Cockpit-Sicht für freigabegesteuerte Projektfunktionsaktivierung."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_authorization import ZCockpitAuthorizationView

_STATUS_LABELS = {
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
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
        risk_class_map: dict[str, str] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.base_assignments = tuple(base_assignments or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}
        self.evaluator = ProjectOSApprovedRoleActivationEvaluator(
            roles=roles,
            activations=activations,
            approval_requests=approval_requests,
            approvals=approvals,
            risk_class_map=risk_class_map,
        )

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        approval_state = self.evaluator.state(project_id=self.project_id, user=self.user, scope=scope, at=at)
        derived = self.evaluator.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        auth = ZCockpitAuthorizationView(self.user, self.base_assignments + derived)
        permissions = sorted({
            item.permission for item in self.base_assignments + derived
            if item.user_id == self.user.user_id and item.scope == scope
        })
        rights = [auth.state(permission, scope=scope, at=at) for permission in permissions]

        def decorate(item: dict[str, Any]) -> dict[str, Any]:
            result = dict(item)
            result["approval"] = dict(result["approval"])
            result["approval"]["status_label"] = _STATUS_LABELS.get(
                result["approval"]["status"], result["approval"]["status"]
            )
            return result

        return {
            "project_id": approval_state["project_id"],
            "user": self.user.as_dict(),
            "scope": scope,
            "effective_activations": [decorate(item) for item in approval_state["effective_activations"]],
            "blocked_activations": [decorate(item) for item in approval_state["blocked_activations"]],
            "pending_post_reviews": [decorate(item) for item in approval_state["pending_post_reviews"]],
            "rights": rights,
            "post_review_required": bool(approval_state["pending_post_reviews"]),
            "read_only": True,
        }
