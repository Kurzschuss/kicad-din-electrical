"""Read-only Laufzeit-Historie erfolgreicher ProjectOS-Benutzerverwaltungs-Commands.

Die Historie ist keine fachliche Wahrheit und wird nicht in Bundle v4 persistiert. Sie
referenziert erfolgreiche Commands und deren Nachweise, ohne Audit oder Domainzustand zu
verändern. Undo/Redo wird auf dieser Basis später als neue Fachänderung ausgeführt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("recorded_at must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("recorded_at must include timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def _freeze(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(values or {}))


@dataclass(frozen=True)
class ProjectOSUserManagementCommandRecord:
    """Unveränderlicher Laufzeitnachweis eines erfolgreich ausgeführten Commands."""

    command_id: str
    project_id: str
    operation: str
    actor_user_id: str | None
    correlation_id: str
    causation_id: str | None
    reference: str
    recorded_at: str
    reversible: bool
    before_values: Mapping[str, Any] = field(default_factory=dict)
    after_values: Mapping[str, Any] = field(default_factory=dict)
    message_id: str | None = None
    audit_reference: str | None = None

    def __post_init__(self) -> None:
        operation = str(self.operation).strip()
        reference = str(self.reference).strip()
        if not operation:
            raise ValueError("operation must not be empty")
        if not reference:
            raise ValueError("reference must not be empty")
        object.__setattr__(self, "command_id", _uuid(self.command_id, "command_id"))
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "correlation_id", _uuid(self.correlation_id, "correlation_id"))
        if self.actor_user_id is not None:
            object.__setattr__(self, "actor_user_id", _uuid(self.actor_user_id, "actor_user_id"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _uuid(self.causation_id, "causation_id"))
        if self.message_id is not None:
            object.__setattr__(self, "message_id", _uuid(self.message_id, "message_id"))
        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "recorded_at", _timestamp(self.recorded_at))
        object.__setattr__(self, "reversible", bool(self.reversible))
        object.__setattr__(self, "before_values", _freeze(self.before_values))
        object.__setattr__(self, "after_values", _freeze(self.after_values))
        if self.audit_reference is not None:
            object.__setattr__(self, "audit_reference", str(self.audit_reference))

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "project_id": self.project_id,
            "operation": self.operation,
            "actor_user_id": self.actor_user_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "reference": self.reference,
            "recorded_at": self.recorded_at,
            "reversible": self.reversible,
            "before_values": dict(self.before_values),
            "after_values": dict(self.after_values),
            "message_id": self.message_id,
            "audit_reference": self.audit_reference,
            "persisted": False,
            "read_only": True,
        }


class ProjectOSUserManagementCommandHistory:
    """Append-only Laufzeithistorie; Lesen verändert weder Historie noch Domainzustand."""

    def __init__(self) -> None:
        self._records: list[ProjectOSUserManagementCommandRecord] = []
        self._command_ids: set[str] = set()

    def append(self, record: ProjectOSUserManagementCommandRecord) -> ProjectOSUserManagementCommandRecord:
        if record.command_id in self._command_ids:
            raise ValueError("command_id already recorded")
        self._records.append(record)
        self._command_ids.add(record.command_id)
        return record

    def all(self) -> tuple[ProjectOSUserManagementCommandRecord, ...]:
        return tuple(self._records)

    def get(self, command_id: str) -> ProjectOSUserManagementCommandRecord | None:
        normalized = _uuid(command_id, "command_id")
        return next((item for item in self._records if item.command_id == normalized), None)

    def latest(self) -> ProjectOSUserManagementCommandRecord | None:
        return self._records[-1] if self._records else None

    def state(self) -> dict[str, Any]:
        latest = self.latest()
        return {
            "count": len(self._records),
            "latest_command_id": latest.command_id if latest is not None else None,
            "latest_operation": latest.operation if latest is not None else None,
            "latest_reversible": latest.reversible if latest is not None else False,
            "persisted": False,
            "read_only": True,
        }

    def clear(self) -> None:
        self._records.clear()
        self._command_ids.clear()
