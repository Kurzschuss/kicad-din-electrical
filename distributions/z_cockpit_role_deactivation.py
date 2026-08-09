"""Read-only Z_Cockpit-Sicht für Beendigung/Rückgabe aktivierter Projektfunktionen."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation, ProjectOSProjectRoleLifecycleEvaluator
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_authorization import ZCockpitAuthorizationView

_END_REASON_LABELS = {
    "manual_return": "Manuelle Rückgabe", "principal_returned": "Projektleiter zurückgekehrt",
    "period_ended": "Zeitraum beendet", "revoked": "Widerrufen", "handover_completed": "Übergabe abgeschlossen",
    "emergency_ended": "Notfall beendet", "succession_completed": "Nachfolge abgeschlossen",
}


class ZCockpitProjectRoleDeactivationView:
    """Zeigt Lebenszyklusstand und simuliert eine Rückgabe ohne Persistenzänderung."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        deactivations: Iterable[ProjectOSProjectRoleDeactivation] | None = None,
        role_terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.deactivations = tuple(deactivations or ())
        self.role_terminations = tuple(role_terminations or ())
        self.base_assignments = tuple(base_assignments or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        lifecycle = ProjectOSProjectRoleLifecycleEvaluator(
            roles=self.roles,
            activations=self.activations,
            deactivations=self.deactivations,
            role_terminations=self.role_terminations,
        )
        lifecycle_state = lifecycle.state(project_id=self.project_id, user=self.user, scope=scope, at=at)
        derived = lifecycle.permission_assignments(
            project_id=self.project_id, user=self.user, permission_map=self.permission_map, scope=scope, at=at
        )
        permissions = sorted({item.permission for item in self.base_assignments + derived if item.user_id == self.user.user_id and item.scope == scope})
        auth = ZCockpitAuthorizationView(self.user, self.base_assignments + derived)
        rights = [auth.state(permission, scope=scope, at=at) for permission in permissions]
        return {
            "project_id": lifecycle_state["project_id"],
            "user": self.user.as_dict(),
            "scope": scope,
            "effective_roles": lifecycle_state["effective_roles"],
            "terminated_assigned_roles": lifecycle_state["terminated_assigned_roles"],
            "effective_activations": lifecycle_state["effective_activations"],
            "ended_activations": [self._ended(item) for item in lifecycle_state["ended_activations"]],
            "rights": rights,
            "read_only": True,
        }

    def simulate_deactivation(
        self,
        deactivation: ProjectOSProjectRoleDeactivation,
        *,
        scope: str = "project",
        before_at: datetime | None = None,
        after_at: datetime | None = None,
    ) -> dict[str, Any]:
        before = self.state(scope=scope, at=before_at)
        simulated = ZCockpitProjectRoleDeactivationView(
            project_id=self.project_id,
            user=self.user,
            roles=self.roles,
            activations=self.activations,
            deactivations=self.deactivations + (deactivation,),
            role_terminations=self.role_terminations,
            base_assignments=self.base_assignments,
            permission_map=self.permission_map,
        )
        after = simulated.state(scope=scope, at=after_at or before_at)
        before_rights = {item["permission"]: item for item in before["rights"]}
        after_rights = {item["permission"]: item for item in after["rights"]}
        impacts = []
        for permission in sorted(set(before_rights) | set(after_rights)):
            b = before_rights.get(permission)
            a = after_rights.get(permission)
            before_allowed = bool(b and b["allowed"])
            after_allowed = bool(a and a["allowed"])
            impacts.append({
                "permission": permission,
                "before": b,
                "after": a,
                "decision_changed": (b or {}).get("decision") != (a or {}).get("decision"),
                "lost_permission": before_allowed and not after_allowed,
                "remained_allowed": before_allowed and after_allowed,
                "remained_denied": bool(a and a["decision"] == "deny"),
            })
        return {
            "project_id": self.project_id,
            "user": self.user.as_dict(),
            "scope": scope,
            "deactivation": self._deactivation(deactivation.as_dict()),
            "before": before,
            "after": after,
            "permission_impacts": impacts,
            "lost_permission_count": sum(1 for item in impacts if item["lost_permission"]),
            "changed_permission_count": sum(1 for item in impacts if item["decision_changed"]),
            "read_only": True,
            "note": "Die Rückgabe-Simulation verändert keine gespeicherten Aktivierungen, Rollenzuweisungs-Beendigungen, Funktionen oder Rechtezuweisungen.",
        }

    @staticmethod
    def _deactivation(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["reason_label"] = _END_REASON_LABELS[item["reason"]]
        return result

    @classmethod
    def _ended(cls, item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["deactivation"] = cls._deactivation(result["deactivation"])
        return result
