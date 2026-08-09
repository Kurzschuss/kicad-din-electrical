"""Expliziter ProjectOS-Lifecycle für die Reaktivierung derselben Benutzeridentität."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _timestamp(value: str, field_name: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSUserReactivation:
    """Reaktiviert eine deaktivierte Benutzeridentität ohne neue user_id."""

    project_id: str
    user_id: str
    reactivated_at: str
    reactivated_by_user_id: str
    reason: str
    source_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    reactivation_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        reason = str(self.reason).strip()
        source_reference = None if self.source_reference is None else str(self.source_reference).strip()
        if not reason:
            raise ValueError("user reactivation reason must not be empty")
        if source_reference == "": source_reference = None
        if not isinstance(self.metadata, dict): raise ValueError("metadata must be an object")
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "reactivated_by_user_id", _uuid(self.reactivated_by_user_id, "reactivated_by_user_id"))
        object.__setattr__(self, "reactivation_id", _uuid(self.reactivation_id, "reactivation_id"))
        object.__setattr__(self, "reactivated_at", _timestamp(self.reactivated_at, "reactivated_at"))
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "source_reference", source_reference)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def is_effective(self, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("user reactivation evaluation time must include timezone")
        return datetime.fromisoformat(self.reactivated_at) <= at.astimezone(timezone.utc)

    def as_dict(self) -> dict[str, Any]:
        return {"reactivation_id": self.reactivation_id, "project_id": self.project_id, "user_id": self.user_id,
                "reactivated_at": self.reactivated_at, "reactivated_by_user_id": self.reactivated_by_user_id,
                "reason": self.reason, "source_reference": self.source_reference, "metadata": dict(self.metadata)}
