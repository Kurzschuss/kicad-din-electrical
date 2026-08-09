"""Read-only Z_Cockpit-Sicht auf den ProjectOS-Benutzer-Deaktivierungs-Lifecycle."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ZCockpitUserLifecycleView:
    def __init__(self, manager) -> None:
        self.manager = manager

    def state(self, *, at: datetime | None = None) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("user lifecycle evaluation time must include timezone")
        current = current.astimezone(timezone.utc)
        state = self.manager.user_management
        deactivation_by_user = {item.user_id: item for item in state.user_deactivations}
        active_users = []
        scheduled_users = []
        deactivated_users = []
        for user in state.users:
            deactivation = deactivation_by_user.get(user.user_id)
            row = {
                "user": user.as_dict(),
                "deactivation": deactivation.as_dict() if deactivation is not None else None,
                "permission_assignment_count": sum(1 for item in state.permission_assignments if item.user_id == user.user_id),
                "project_role_count": sum(1 for item in state.project_roles if item.user_id == user.user_id),
            }
            if deactivation is None:
                row["lifecycle_status"] = "active"
                active_users.append(row)
            elif deactivation.is_effective(current):
                row["lifecycle_status"] = "deactivated"
                deactivated_users.append(row)
            else:
                row["lifecycle_status"] = "scheduled_deactivation"
                scheduled_users.append(row)
        return {
            "project_id": state.project_id,
            "evaluated_at": current.isoformat(),
            "active_users": active_users,
            "scheduled_deactivations": scheduled_users,
            "deactivated_users": deactivated_users,
            "active_user_count": len(active_users),
            "scheduled_deactivation_count": len(scheduled_users),
            "deactivated_user_count": len(deactivated_users),
            "historical_assignments_preserved": True,
            "user_identity_deletion": False,
            "read_only": True,
            "persisted": False,
            "note": "Deaktivierung beendet die Rechtewirkung, nicht die Benutzeridentität. Historische Rechte- und Rollenbezüge bleiben sichtbar.",
        }
