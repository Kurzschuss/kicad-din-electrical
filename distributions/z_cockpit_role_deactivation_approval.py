"""Read-only Z_Cockpit-Sicht für freigabegesteuerte Rollenrückgaben."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_deactivation_approval import ProjectOSApprovedRoleDeactivationEvaluator
from .projectos_user_project_roles import ProjectOSUserProjectRole

_STATUS_LABELS = {
    "approval_missing": "Freigabeauftrag fehlt",
    "pending_approval": "Freigabe ausstehend",
    "approved": "Freigegeben",
    "approved_not_required": "Keine zweite Freigabe erforderlich",
    "rejected": "Abgelehnt",
    "emergency_pending_review": "Notfall vorläufig wirksam – Nachprüfung erforderlich",
}


class ZCockpitRoleDeactivationApprovalView:
    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        deactivations: Iterable[ProjectOSProjectRoleDeactivation] | None = None,
        role_terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
            roles=roles,
            activations=activations,
            deactivations=deactivations,
            role_terminations=role_terminations,
            approval_requests=approval_requests,
            approvals=approvals,
        )

    def state(self, *, scope: str = "project", at: datetime | None = None, risk_class: str = "low") -> dict[str, Any]:
        state = self.evaluator.state(project_id=self.project_id, user=self.user, scope=scope, at=at, risk_class=risk_class)
        items = []
        for entry in state["approval_states"]:
            approval = entry["approval"]
            status = approval["status"]
            items.append({
                "deactivation": entry["deactivation"],
                "approval_status": status,
                "approval_status_label": _STATUS_LABELS[status],
                "effective": bool(approval["effective"]),
                "post_review_required": bool(approval.get("post_review_required")),
                "attention_required": status in {"approval_missing", "pending_approval", "rejected", "emergency_pending_review"},
                "approval": approval,
            })
        return {
            "project_id": state["project_id"],
            "user": state["user"],
            "scope": scope,
            "risk_class": risk_class,
            "effective_roles": state["effective_roles"],
            "terminated_assigned_roles": state["terminated_assigned_roles"],
            "blocked_deactivations": state["blocked_deactivations"],
            "pending_post_reviews": state["pending_post_reviews"],
            "deactivation_approvals": items,
            "attention_required": any(item["attention_required"] for item in items),
            "read_only": True,
        }
