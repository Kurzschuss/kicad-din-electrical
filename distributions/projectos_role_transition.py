"""Read-only Simulation projektbezogener Funktionswechsel und ihrer Rechteauswirkungen."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_project_roles import ProjectOSUserProjectRole, ProjectOSUserProjectRoleRegistry
from .z_cockpit_authorization import ZCockpitAuthorizationView


class ProjectOSProjectRoleTransitionSimulator:
    """Vergleicht aktuellen und hypothetischen Projektfunktionsstand ohne Persistenzänderung."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        role_terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
    ) -> None:
        self.project_id = project_id
        self.user = user
        self.roles = tuple(roles or ())
        self.role_terminations = tuple(role_terminations or ())
        self.base_assignments = tuple(base_assignments or ())
        self.permission_map = {key: tuple(values) for key, values in (permission_map or {}).items()}

    def simulate(
        self,
        *,
        add_roles: Iterable[ProjectOSUserProjectRole] | None = None,
        remove_role_assignment_ids: Iterable[str] | None = None,
        permissions: Iterable[str] | None = None,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        remove_ids = set(remove_role_assignment_ids or ())
        additions = tuple(add_roles or ())
        simulated_roles = tuple(role for role in self.roles if role.role_assignment_id not in remove_ids) + additions
        simulated_terminations = tuple(
            item for item in self.role_terminations if item.role_assignment_id not in remove_ids
        )
        baseline_registry = ProjectOSUserProjectRoleRegistry(self.roles, self.role_terminations)
        simulated_registry = ProjectOSUserProjectRoleRegistry(simulated_roles, simulated_terminations)
        baseline_derived = baseline_registry.permission_assignments(
            project_id=self.project_id, user=self.user, permission_map=self.permission_map, scope=scope, at=at
        )
        simulated_derived = simulated_registry.permission_assignments(
            project_id=self.project_id, user=self.user, permission_map=self.permission_map, scope=scope, at=at
        )
        permission_set = set(permissions or ())
        permission_set.update(item.permission for item in self.base_assignments + baseline_derived + simulated_derived if item.user_id == self.user.user_id and item.scope == scope)
        baseline_view = ZCockpitAuthorizationView(self.user, self.base_assignments + baseline_derived)
        simulated_view = ZCockpitAuthorizationView(self.user, self.base_assignments + simulated_derived)
        impacts = []
        for permission in sorted(permission_set):
            before = baseline_view.state(permission, scope=scope, at=at)
            after = simulated_view.state(permission, scope=scope, at=at)
            impacts.append({
                "permission": permission,
                "before": before,
                "after": after,
                "decision_changed": before["decision"] != after["decision"],
                "became_allowed": not before["allowed"] and after["allowed"],
                "became_denied": before["allowed"] and not after["allowed"],
            })
        return {
            "project_id": self.project_id,
            "user": self.user.as_dict(),
            "scope": scope,
            "baseline_roles": baseline_registry.state(project_id=self.project_id, user=self.user, scope=scope, at=at),
            "simulated_roles": simulated_registry.state(project_id=self.project_id, user=self.user, scope=scope, at=at),
            "removed_role_assignment_ids": sorted(remove_ids),
            "added_role_assignment_ids": [role.role_assignment_id for role in additions],
            "permission_impacts": impacts,
            "changed_permission_count": sum(1 for item in impacts if item["decision_changed"]),
            "read_only": True,
            "note": "Die Funktionswechsel-Simulation verändert keine gespeicherten Benutzerfunktionen, Beendigungen oder Rechtezuweisungen.",
        }
