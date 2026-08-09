"""Read-only Z_Cockpit-Sicht und Vorab-Simulation für Rollenzuweisungs-Beendigungen."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_user_project_roles import ProjectOSUserProjectRole

_STATUS_LABELS = {
    "risk_not_configured": "Risikoklasse nicht konfiguriert",
    "approval_missing": "Freigabeauftrag fehlt",
    "pending_approval": "Freigabe ausstehend",
    "approved": "Freigegeben",
    "approved_not_required": "Keine zweite Freigabe erforderlich",
    "rejected": "Abgelehnt",
    "emergency_pending_review": "Notfall vorläufig wirksam – Nachprüfung erforderlich",
}


def _timestamp(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


class ZCockpitRoleAssignmentTerminationView:
    """Zeigt Freigabestatus und simuliert eine Beendigung ohne Domainmutation."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        permission_map: Mapping[str, Iterable[str]] | None = None,
        risk_class_map: Mapping[str, str] | None = None,
    ) -> None:
        self.project_id = str(project_id)
        self.user = user
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.terminations = tuple(terminations or ())
        self.approval_requests = tuple(approval_requests or ())
        self.approvals = tuple(approvals or ())
        self.permission_map = {
            str(role): tuple(str(permission) for permission in permissions)
            for role, permissions in (permission_map or {}).items()
        }
        self.risk_class_map = {
            str(role).strip(): str(risk).strip().lower()
            for role, risk in (risk_class_map or {}).items()
            if str(role).strip()
        }
        self.evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
            roles=self.roles,
            terminations=self.terminations,
            approval_requests=self.approval_requests,
            approvals=self.approvals,
            risk_class_map=self.risk_class_map,
        )

    def _current_role_permissions(
        self,
        role_assignment_id: str,
        *,
        scope: str,
        at: datetime,
    ) -> list[str]:
        evaluator = ProjectOSApprovedRoleActivationEvaluator(
            roles=self.roles,
            activations=self.activations,
            role_terminations=self.terminations,
            approval_requests=self.approval_requests,
            approvals=self.approvals,
            risk_class_map=self.risk_class_map,
        )
        assignments = evaluator.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        return sorted({
            item.permission
            for item in assignments
            if item.metadata.get("role_assignment_id") == role_assignment_id
        })

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("Z_Cockpit evaluation time must include timezone")
        current = current.astimezone(timezone.utc)
        raw = self.evaluator.state(project_id=self.project_id, user=self.user, scope=scope, at=current)

        def decorate(item: dict[str, Any]) -> dict[str, Any]:
            row = dict(item)
            row["approval"] = dict(row["approval"])
            status = row["approval"].get("status")
            row["approval"]["status_label"] = _STATUS_LABELS.get(status, str(status))
            return row

        states = [decorate(item) for item in raw["termination_states"]]
        blocked = [decorate(item) for item in raw["blocked_terminations"]]
        scheduled = [decorate(item) for item in raw["scheduled_terminations"]]
        pending_reviews = [decorate(item) for item in raw["pending_post_reviews"]]
        return {
            "project_id": raw["project_id"],
            "user": raw["user"],
            "scope": scope,
            "evaluated_at": raw["evaluated_at"],
            "termination_states": states,
            "effective_terminations": list(raw["effective_terminations"]),
            "blocked_terminations": blocked,
            "scheduled_terminations": scheduled,
            "pending_post_reviews": pending_reviews,
            "configuration_required": bool(raw["configuration_required"]),
            "attention_required": bool(blocked or pending_reviews or raw["configuration_required"]),
            "read_only": True,
            "persisted": False,
        }

    def simulate_candidate(
        self,
        *,
        role_assignment_id: str,
        ended_at: str,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("Z_Cockpit simulation time must include timezone")
        current = current.astimezone(timezone.utc)
        ended = _timestamp(ended_at, "ended_at")
        matches = [
            role for role in self.roles
            if role.role_assignment_id == role_assignment_id
            and role.project_id == self.project_id
            and role.user_id == self.user.user_id
            and role.scope == scope
        ]
        if len(matches) != 1:
            raise ValueError("role assignment simulation target is unknown or ambiguous")
        role = matches[0]
        risk_class = self.risk_class_map.get(role.role_type)
        permissions = self._current_role_permissions(role.role_assignment_id, scope=scope, at=current)
        scheduled = ended > current

        if risk_class is None:
            status = "risk_not_configured"
            approval_required = False
            configuration_required = True
            effective_without_approval = False
            next_action = "configure_role_risk"
        elif risk_class in {"high", "critical"}:
            status = "approval_required"
            approval_required = True
            configuration_required = False
            effective_without_approval = False
            next_action = "request_role_assignment_termination_approval"
        else:
            status = "approved_not_required"
            approval_required = False
            configuration_required = False
            effective_without_approval = True
            next_action = "execute_termination"

        return {
            "project_id": self.project_id,
            "user_id": self.user.user_id,
            "role_assignment_id": role.role_assignment_id,
            "role_type": role.role_type,
            "scope": scope,
            "risk_class": risk_class,
            "ended_at": ended.isoformat(),
            "evaluated_at": current.isoformat(),
            "scheduled": scheduled,
            "status": status,
            "approval_action_type": "role_assignment_termination",
            "approval_required": approval_required,
            "configuration_required": configuration_required,
            "would_be_effective_when_due_without_new_approval": effective_without_approval,
            "would_be_effective_now_without_new_approval": bool(not scheduled and effective_without_approval),
            "potential_lost_permissions": permissions,
            "next_action": next_action,
            "domain_mutation": False,
            "read_only": True,
            "persisted": False,
        }
