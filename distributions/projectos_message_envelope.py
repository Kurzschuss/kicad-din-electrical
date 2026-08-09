"""Transportneutraler ProjectOS-Nachrichtenumschlag mit Projektkorrelation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from .din_editor_project_context import DinEditorProjectContext


_ALLOWED_MESSAGE_TYPES = {
    "command",
    "event",
    "request",
    "response",
    "notification",
    "error",
    "security_event",
    "system_state",
}


def _normalize_uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _normalize_timestamp(value: datetime | None) -> str:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSMessageEnvelope:
    """Broker-unabhängiger Umschlag für ProjectOS-Nachrichten."""

    message_type: str
    name: str
    project_id: str
    payload: dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    causation_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: int = 1

    def __post_init__(self) -> None:
        message_type = str(self.message_type).strip()
        if message_type not in _ALLOWED_MESSAGE_TYPES:
            raise ValueError(f"unsupported message_type: {message_type}")
        name = str(self.name).strip()
        if not name:
            raise ValueError("message name is required")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be an object")
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")

        object.__setattr__(self, "message_type", message_type)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "project_id", _normalize_uuid(self.project_id, "project_id"))
        object.__setattr__(self, "message_id", _normalize_uuid(self.message_id, "message_id"))
        object.__setattr__(self, "correlation_id", _normalize_uuid(self.correlation_id, "correlation_id"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _normalize_uuid(self.causation_id, "causation_id"))

        parsed = datetime.fromisoformat(str(self.timestamp).replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        object.__setattr__(self, "timestamp", parsed.astimezone(timezone.utc).isoformat())

    @classmethod
    def from_project_context(
        cls,
        context: DinEditorProjectContext,
        *,
        message_type: str,
        name: str,
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        timestamp: datetime | None = None,
    ) -> "ProjectOSMessageEnvelope":
        return cls(
            message_type=message_type,
            name=name,
            project_id=context.project_id,
            payload=dict(payload or {}),
            correlation_id=correlation_id or str(uuid4()),
            causation_id=causation_id,
            timestamp=_normalize_timestamp(timestamp),
        )

    def child(
        self,
        *,
        message_type: str,
        name: str,
        payload: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> "ProjectOSMessageEnvelope":
        """Erzeuge eine kausal abhängige Nachricht im selben Vorgang."""
        return ProjectOSMessageEnvelope(
            message_type=message_type,
            name=name,
            project_id=self.project_id,
            payload=dict(payload or {}),
            correlation_id=self.correlation_id,
            causation_id=self.message_id,
            timestamp=_normalize_timestamp(timestamp),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "message_id": self.message_id,
            "message_type": self.message_type,
            "name": self.name,
            "project_id": self.project_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp": self.timestamp,
            "payload": dict(self.payload),
        }
