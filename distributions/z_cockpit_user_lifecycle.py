"""Read-only Z_Cockpit-Sicht auf den chronologischen ProjectOS-Benutzer-Lifecycle."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .projectos_user_lifecycle import ProjectOSUserLifecycleEvaluator


class ZCockpitUserLifecycleView:
    def __init__(self, manager) -> None:
        self.manager = manager

    def state(self, *, at: datetime | None = None) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("user lifecycle evaluation time must include timezone")
        current = current.astimezone(timezone.utc)
        state = self.manager.user_management
        evaluator = ProjectOSUserLifecycleEvaluator(
            deactivations=state.user_deactivations,
            reactivations=state.user_reactivations,
        )
        active_users = []
        deactivated_users = []
        scheduled_deactivations = []
        scheduled_reactivations = []

        for user in state.users:
            lifecycle = evaluator.state(user_id=user.user_id, at=current)
            future_deactivations = sorted(
                [item for item in state.user_deactivations if item.user_id == user.user_id and not item.is_effective(current)],
                key=lambda item: item.deactivated_at,
            )
            future_reactivations = sorted(
                [item for item in state.user_reactivations if item.user_id == user.user_id and not item.is_effective(current)],
                key=lambda item: item.reactivated_at,
            )
            row = {
                "user": user.as_dict(),
                "lifecycle_status": lifecycle["status"],
                "latest_event_type": lifecycle["latest_event_type"],
                "latest_event": lifecycle["latest_event"],
                "event_history": lifecycle["event_history"],
                "event_count": lifecycle["event_count"],
                "permission_assignment_count": sum(1 for item in state.permission_assignments if item.user_id == user.user_id),
                "project_role_count": sum(1 for item in state.project_roles if item.user_id == user.user_id),
                "future_deactivations": [item.as_dict() for item in future_deactivations],
                "future_reactivations": [item.as_dict() for item in future_reactivations],
            }
            if lifecycle["deactivated"]:
                deactivated_users.append(row)
            else:
                active_users.append(row)
            scheduled_deactivations.extend(
                {"user": user.as_dict(), "deactivation": item.as_dict()}
                for item in future_deactivations
            )
            scheduled_reactivations.extend(
                {"user": user.as_dict(), "reactivation": item.as_dict()}
                for item in future_reactivations
            )

        return {
            "project_id": state.project_id,
            "evaluated_at": current.isoformat(),
            "active_users": active_users,
            "deactivated_users": deactivated_users,
            "scheduled_deactivations": scheduled_deactivations,
            "scheduled_reactivations": scheduled_reactivations,
            "active_user_count": len(active_users),
            "deactivated_user_count": len(deactivated_users),
            "scheduled_deactivation_count": len(scheduled_deactivations),
            "scheduled_reactivation_count": len(scheduled_reactivations),
            "user_deactivation_event_count": len(state.user_deactivations),
            "user_reactivation_event_count": len(state.user_reactivations),
            "historical_assignments_preserved": True,
            "user_identity_deletion": False,
            "read_only": True,
            "persisted": False,
            "note": "Deaktivierung und Reaktivierung sind historische Ereignisse derselben user_id. Der aktuelle Status folgt der chronologischen Ereigniskette; Rechte- und Rollenbezüge bleiben erhalten.",
        }
