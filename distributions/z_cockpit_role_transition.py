"""Read-only Projektleiteransicht für simulierte Benutzer-Funktionswechsel."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_transition import ProjectOSProjectRoleTransitionSimulator
from .projectos_user_project_roles import ProjectOSUserProjectRole

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
_RISK_LABELS = {"low": "Niedrig", "medium": "Mittel", "high": "Hoch", "critical": "Kritisch"}
_ROLE_LABELS = {
    "project_lead": "Projektleiter",
    "deputy": "Stellvertretung",
    "trusted_person": "Vertrauensperson",
    "successor": "Nachfolger",
}


class ZCockpitProjectRoleTransitionView:
    """Bereitet eine Funktionswechsel-Simulation verständlich für Projektleiter auf."""

    def __init__(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        base_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        permission_map: dict[str, Iterable[str]] | None = None,
    ) -> None:
        self._simulator = ProjectOSProjectRoleTransitionSimulator(
            project_id=project_id,
            user=user,
            roles=roles,
            base_assignments=base_assignments,
            permission_map=permission_map,
        )

    def simulate(
        self,
        *,
        add_roles: Iterable[ProjectOSUserProjectRole] | None = None,
        remove_role_assignment_ids: Iterable[str] | None = None,
        permissions: Iterable[str] | None = None,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        raw = self._simulator.simulate(
            add_roles=add_roles,
            remove_role_assignment_ids=remove_role_assignment_ids,
            permissions=permissions,
            scope=scope,
            at=at,
        )
        impacts = [self._decorate_impact(item) for item in raw["permission_impacts"]]
        gained = [item for item in impacts if item["became_allowed"]]
        lost = [item for item in impacts if item["became_denied"]]
        changed = [item for item in impacts if item["decision_changed"]]
        deny_conflicts = [item for item in impacts if item["deny_conflict_after"]]
        highest_risk = self._highest_risk(impacts)
        return {
            "project_id": raw["project_id"],
            "user": raw["user"],
            "scope": raw["scope"],
            "baseline_roles": self._roles(raw["baseline_roles"]["active_roles"]),
            "simulated_roles": self._roles(raw["simulated_roles"]["active_roles"]),
            "added_role_assignment_ids": raw["added_role_assignment_ids"],
            "removed_role_assignment_ids": raw["removed_role_assignment_ids"],
            "permission_impacts": impacts,
            "gained_permissions": [item["permission"] for item in gained],
            "lost_permissions": [item["permission"] for item in lost],
            "changed_permission_count": len(changed),
            "deny_conflicts": deny_conflicts,
            "deny_conflict_count": len(deny_conflicts),
            "highest_risk_class": highest_risk,
            "highest_risk_label": _RISK_LABELS[highest_risk] if highest_risk else None,
            "summary": self._summary(gained, lost, deny_conflicts, highest_risk),
            "read_only": True,
            "note": raw["note"],
        }

    @staticmethod
    def _roles(roles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                **role,
                "role_label": _ROLE_LABELS.get(role["role_type"], role["role_type"]),
            }
            for role in roles
        ]

    def _decorate_impact(self, item: dict[str, Any]) -> dict[str, Any]:
        before = item["before"]
        after = item["after"]
        risk_classes = [
            source["risk_class"]
            for state in (before, after)
            for source in state.get("sources", [])
            if source.get("active")
        ]
        risk = max(risk_classes, key=lambda value: _RISK_ORDER[value]) if risk_classes else None
        deny_conflict_after = after["decision"] == "deny" and any(
            source["effect"] == "allow" for source in after.get("sources", [])
        )
        return {
            **item,
            "risk_class": risk,
            "risk_label": _RISK_LABELS[risk] if risk else None,
            "deny_conflict_after": deny_conflict_after,
        }

    @staticmethod
    def _highest_risk(impacts: list[dict[str, Any]]) -> str | None:
        risks = [item["risk_class"] for item in impacts if item["decision_changed"] and item["risk_class"]]
        return max(risks, key=lambda value: _RISK_ORDER[value]) if risks else None

    @staticmethod
    def _summary(
        gained: list[dict[str, Any]],
        lost: list[dict[str, Any]],
        deny_conflicts: list[dict[str, Any]],
        highest_risk: str | None,
    ) -> str:
        parts = []
        if gained:
            parts.append(f"{len(gained)} Recht(e) würden wirksam hinzukommen")
        if lost:
            parts.append(f"{len(lost)} Recht(e) würden entfallen")
        if deny_conflicts:
            parts.append(f"{len(deny_conflicts)} DENY-Konflikt(e) bleiben wirksam")
        if not parts:
            return "Der simulierte Funktionswechsel verändert keine effektive Rechteentscheidung."
        text = "; ".join(parts) + "."
        if highest_risk:
            text += f" Höchste betroffene Risikoklasse: {_RISK_LABELS[highest_risk]}."
        return text
