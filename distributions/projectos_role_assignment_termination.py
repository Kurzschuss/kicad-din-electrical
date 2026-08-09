"""Expliziter Lifecycle für die Beendigung einer ProjectOS-Rollenzuweisung."""
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
class ProjectOSProjectRoleAssignmentTermination:
    """Beendet eine Rollenzuweisung, ohne die historische Zuweisung zu löschen."""

    role_assignment_id: str
    project_id: str
    user_id: str
    scope: str
    ended_at: str
    ended_by_user_id: str
    reason: str
    source_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    termination_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        scope = str(self.scope).strip()
        reason = str(self.reason).strip()
        source_reference = None if self.source_reference is None else str(self.source_reference).strip()
        if not scope:
            raise ValueError("scope must not be empty")
        if not reason:
            raise ValueError("role assignment termination reason must not be empty")
        if source_reference == "":
            source_reference = None
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "role_assignment_id", _uuid(self.role_assignment_id, "role_assignment_id"))
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "ended_by_user_id", _uuid(self.ended_by_user_id, "ended_by_user_id"))
        object.__setattr__(self, "termination_id", _uuid(self.termination_id, "termination_id"))
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "ended_at", _timestamp(self.ended_at, "ended_at"))
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "source_reference", source_reference)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def is_effective(self, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("role assignment termination evaluation time must include timezone")
        return datetime.fromisoformat(self.ended_at) <= at.astimezone(timezone.utc)

    def as_dict(self) -> dict[str, Any]:
        return {
            "termination_id": self.termination_id,
            "role_assignment_id": self.role_assignment_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "scope": self.scope,
            "ended_at": self.ended_at,
            "ended_by_user_id": self.ended_by_user_id,
            "reason": self.reason,
            "source_reference": self.source_reference,
            "metadata": dict(self.metadata),
        }
