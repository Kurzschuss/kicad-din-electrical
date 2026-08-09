"""Read-only Auswertung chronologischer ProjectOS-Benutzer-De-/Reaktivierungen."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .projectos_user_deactivation import ProjectOSUserDeactivation
from .projectos_user_reactivation import ProjectOSUserReactivation


class ProjectOSUserLifecycleEvaluator:
    """Validiert und bewertet eine alternierende Benutzer-Lifecycle-Ereigniskette."""

    def __init__(self, *, deactivations: Iterable[ProjectOSUserDeactivation] | None = None,
                 reactivations: Iterable[ProjectOSUserReactivation] | None = None) -> None:
        self.deactivations = tuple(deactivations or ())
        self.reactivations = tuple(reactivations or ())
        self._validate_chains()

    @staticmethod
    def _event_time(event) -> datetime:
        value = event.deactivated_at if isinstance(event, ProjectOSUserDeactivation) else event.reactivated_at
        return datetime.fromisoformat(value).astimezone(timezone.utc)

    def _events(self, user_id: str):
        rows = [(self._event_time(item), "deactivated", item) for item in self.deactivations if item.user_id == user_id]
        rows += [(self._event_time(item), "reactivated", item) for item in self.reactivations if item.user_id == user_id]
        rows.sort(key=lambda item: item[0])
        return rows

    def _validate_chains(self) -> None:
        user_ids = {item.user_id for item in self.deactivations} | {item.user_id for item in self.reactivations}
        for user_id in user_ids:
            events = self._events(user_id)
            timestamps = [item[0] for item in events]
            if len(timestamps) != len(set(timestamps)):
                raise ValueError("user lifecycle events must have distinct timestamps")
            active = True
            for _, event_type, _ in events:
                if event_type == "deactivated":
                    if not active:
                        raise ValueError("user lifecycle cannot deactivate an already deactivated user")
                    active = False
                else:
                    if active:
                        raise ValueError("user lifecycle cannot reactivate an active user")
                    active = True

    def state(self, *, user_id: str, at: datetime | None = None) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("user lifecycle evaluation time must include timezone")
        current = current.astimezone(timezone.utc)
        events = [item for item in self._events(user_id) if item[0] <= current]
        active = True
        latest = None
        history = []
        for event_time, event_type, event in events:
            active = event_type == "reactivated"
            latest = (event_type, event)
            history.append({"event_type": event_type, "timestamp": event_time.isoformat(), "event": event.as_dict()})
        return {
            "user_id": user_id,
            "evaluated_at": current.isoformat(),
            "status": "active" if active else "deactivated",
            "active": active,
            "deactivated": not active,
            "latest_event_type": latest[0] if latest is not None else None,
            "latest_event": latest[1].as_dict() if latest is not None else None,
            "event_history": history,
            "event_count": len(history),
            "read_only": True,
        }
