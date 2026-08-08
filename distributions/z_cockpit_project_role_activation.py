"""Read-only Z_Cockpit-Sicht für Projektfunktionsaktivierung und deren Rechteauswirkung."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .projectos_role_activation import ProjectOSProjectRoleActivation, ProjectOSProjectRoleActivationRegistry
from .z_cockpit_authorization import ZCockpitAuthorizationView

_ROLE_LABELS = {
    "project_lead": "Projektleiter",
    "deputy": "Stellvertretung",
    "trusted_person": "Vertrauensperson",
    "successor": "Nachfolger",
}
_REASON_LABELS = {
    "manual": "Manuell",
    "absence": "Abwesenheit",
    "incapacity": "Handlungsunfähigkeit",
    "vacation": "Urlaub",
    "emergency": "Notfall",
    "succession": "Nachfolge",
    "temporary_transfer": "Temporäre Übertragung",
}


class ZCockpitProjectRoleActivationView:
    """Bereitet Aktivierungsstatus und hypothetische Aktivierungen für Z_Cockpit auf."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.base_assignments = tuple(base_assignments or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}

    def state(self, *, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        registry = ProjectOSProjectRoleActivationRegistry(self.roles, self.activations)
        state = registry.state(project_id=self.project_id, user=self.user, scope=scope, at=at)
        derived = registry.permission_assignments(
            project_id=self.project_id,
            user=self.user,
            permission_map=self.permission_map,
            scope=scope,
            at=at,
        )
        permissions = sorted({item.permission for item in self.base_assignments + derived if item.user_id == self.user.user_id and item.scope == scope})
        auth = ZCockpitAuthorizationView(self.user, self.base_assignments + derived)
        rights = [auth.state(permission, scope=scope, at=at) for permission in permissions]
        return {
            "project_id": state["project_id"],
            "user": self.user.as_dict(),
            "scope": scope,
            "active_roles": [self._role(item) for item in state["active_roles"]],
            "assigned_not_activated_roles": [self._role(item) for item in state["assigned_not_activated_roles"]],
            "inactive_activations": [self._activation(item) for item in state["inactive_activations"]],
            "rights": rights,
            "read_only": True,
        }

    def simulate_activation(
        self,
        activation: ProjectOSProjectRoleActivation,
        *,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        before = self.state(scope=scope, at=at)
        simulated_view = ZCockpitProjectRoleActivationView(
            project_id=self.project_id,
            user=self.user,
            roles=self.roles,
            activations=self.activations + (activation,),
            base_assignments=self.base_assignments,
            permission_map=self.permission_map,
        )
        after = simulated_view.state(scope=scope, at=at)
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
                "became_allowed": not before_allowed and after_allowed,
                "became_denied": before_allowed and not after_allowed,
                "deny_conflict": bool(a and a["decision"] == "deny" and any(src["effect"] == "allow" for src in a["sources"])),
            })
        return {
            "project_id": self.project_id,
            "user": self.user.as_dict(),
            "scope": scope,
            "activation": self._activation(activation.as_dict()),
            "before": before,
            "after": after,
            "permission_impacts": impacts,
            "changed_permission_count": sum(1 for item in impacts if item["decision_changed"]),
            "read_only": True,
            "note": "Die Aktivierungssimulation verändert keine gespeicherten Funktionen, Aktivierungen oder Rechtezuweisungen.",
        }

    @staticmethod
    def _role(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["role_label"] = _ROLE_LABELS[item["role_type"]]
        if "activation" in result and result["activation"]:
            result["activation"] = ZCockpitProjectRoleActivationView._activation(result["activation"])
        return result

    @staticmethod
    def _activation(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result["reason_label"] = _REASON_LABELS[item["reason"]]
        return result
