"""Read-only Z_Cockpit-Sicht für projektbezogene Benutzerfunktionen und deren Rechtewirkung."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_user_project_roles import ProjectOSUserProjectRole, ProjectOSUserProjectRoleRegistry
from .z_cockpit_authorization import ZCockpitAuthorizationView

_ROLE_LABELS = {
    "project_lead": "Projektleiter",
    "deputy": "Stellvertretung",
    "trusted_person": "Vertrauensperson",
    "successor": "Nachfolger",
}


class ZCockpitUserProjectRoleView:
    """Zeigt Funktionen, Herkunft und daraus abgeleitete Rechte ohne Zustandsänderung."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.registry = ProjectOSUserProjectRoleRegistry(roles)
        self.base_assignments = tuple(base_assignments or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        role_state = self.registry.state(project_id=self.project_id, user=self.user, scope=scope, at=at)
        derived = self.registry.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        permissions = sorted({item.permission for item in self.base_assignments + derived if item.user_id == self.user.user_id and item.scope == scope})
        authorization = ZCockpitAuthorizationView(self.user, self.base_assignments + derived)
        return {
            "project_id": role_state["project_id"],
            "user": role_state["user"],
            "scope": scope,
            "evaluated_at": role_state["evaluated_at"],
            "active_roles": [self._decorate_role(item, active=True) for item in role_state["active_roles"]],
            "inactive_roles": [self._decorate_role(item, active=False) for item in role_state["inactive_roles"]],
            "derived_assignments": [item.as_dict() for item in derived],
            "permissions": [authorization.state(permission, scope=scope, at=at) for permission in permissions],
            "weight": self.user.weight,
            "weight_used_for_decision": False,
            "read_only": True,
        }

    def simulate_roles(
        self,
        *,
        hypothetical_roles: Iterable[ProjectOSUserProjectRole],
        permission: str,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        baseline_roles = tuple(self.registry._roles)
        baseline_derived = self.registry.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        simulated_registry = ProjectOSUserProjectRoleRegistry(baseline_roles + tuple(hypothetical_roles))
        simulated_derived = simulated_registry.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        baseline = ZCockpitAuthorizationView(self.user, self.base_assignments + baseline_derived).state(permission, scope=scope, at=at)
        simulated = ZCockpitAuthorizationView(self.user, self.base_assignments + simulated_derived).state(permission, scope=scope, at=at)
        return {
            "permission": permission,
            "scope": scope,
            "baseline": baseline,
            "simulated": simulated,
            "decision_changed": baseline["decision"] != simulated["decision"],
            "added_role_count": len(tuple(hypothetical_roles)),
            "read_only": True,
            "note": "Die Simulation ergänzt Projektfunktionen nur hypothetisch und verändert keine gespeicherten Zuordnungen.",
        }

    @staticmethod
    def _decorate_role(item: dict[str, Any], *, active: bool) -> dict[str, Any]:
        result = dict(item)
        result["role_label"] = _ROLE_LABELS[item["role_type"]]
        result["active"] = active
        return result
