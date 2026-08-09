"""Read-only Laufzeit-Historie erfolgreicher ProjectOS-Benutzerverwaltungs-Commands.

Die Historie ist keine fachliche Wahrheit und wird nicht in Bundle v4 persistiert. Sie
referenziert erfolgreiche Commands und deren Nachweise, ohne Audit oder Domainzustand zu
verändern. Undo/Redo wird auf dieser Basis als neue Fachänderung ausgeführt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Mapping
from uuid import UUID

_HISTORY_ACTIONS = {"command", "undo", "redo"}


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
    history_action: str = "command"
    related_command_id: str | None = None
    before_values: Mapping[str, Any] = field(default_factory=dict)
    after_values: Mapping[str, Any] = field(default_factory=dict)
    message_id: str | None = None
    audit_reference: str | None = None

    def __post_init__(self) -> None:
        operation = str(self.operation).strip()
        reference = str(self.reference).strip()
        history_action = str(self.history_action).strip().lower()
        if not operation:
            raise ValueError("operation must not be empty")
        if not reference:
            raise ValueError("reference must not be empty")
        if history_action not in _HISTORY_ACTIONS:
            raise ValueError(f"unsupported history_action: {history_action}")
        object.__setattr__(self, "command_id", _uuid(self.command_id, "command_id"))
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "correlation_id", _uuid(self.correlation_id, "correlation_id"))
        if self.actor_user_id is not None:
            object.__setattr__(self, "actor_user_id", _uuid(self.actor_user_id, "actor_user_id"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _uuid(self.causation_id, "causation_id"))
        if self.message_id is not None:
            object.__setattr__(self, "message_id", _uuid(self.message_id, "message_id"))
        related_command_id = self.related_command_id
        if history_action in {"undo", "redo"}:
            if related_command_id is None:
                raise ValueError(f"{history_action} requires related_command_id")
            related_command_id = _uuid(related_command_id, "related_command_id")
        elif related_command_id is not None:
            raise ValueError("command history_action must not define related_command_id")
        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "recorded_at", _timestamp(self.recorded_at))
        object.__setattr__(self, "reversible", bool(self.reversible))
        object.__setattr__(self, "history_action", history_action)
        object.__setattr__(self, "related_command_id", related_command_id)
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
            "history_action": self.history_action,
            "related_command_id": self.related_command_id,
            "before_values": dict(self.before_values),
            "after_values": dict(self.after_values),
            "message_id": self.message_id,
            "audit_reference": self.audit_reference,
            "persisted": False,
            "read_only": True,
        }


class ProjectOSUserManagementCommandHistory:
    """Append-only Laufzeithistorie mit linearer, fail-closed Undo-/Redo-Sicht."""

    def __init__(self) -> None:
        self._records: list[ProjectOSUserManagementCommandRecord] = []
        self._command_ids: set[str] = set()
        self._runtime_generation_provider: Callable[[], int] | None = None
        self._runtime_generation: int | None = None

    def bind_runtime_generation(self, provider: Callable[[], int]) -> None:
        self._runtime_generation_provider = provider
        self._runtime_generation = int(provider())

    def _align_runtime_generation(self) -> None:
        if self._runtime_generation_provider is None:
            return
        current = int(self._runtime_generation_provider())
        if current == self._runtime_generation:
            return
        self._records.clear()
        self._command_ids.clear()
        self._runtime_generation = current

    def append(self, record: ProjectOSUserManagementCommandRecord) -> ProjectOSUserManagementCommandRecord:
        self._align_runtime_generation()
        if record.command_id in self._command_ids:
            raise ValueError("command_id already recorded")
        if record.related_command_id is not None and record.related_command_id not in self._command_ids:
            raise ValueError("related_command_id is not present in command history")
        self._records.append(record)
        self._command_ids.add(record.command_id)
        return record

    def all(self) -> tuple[ProjectOSUserManagementCommandRecord, ...]:
        self._align_runtime_generation()
        return tuple(self._records)

    def get(self, command_id: str) -> ProjectOSUserManagementCommandRecord | None:
        self._align_runtime_generation()
        normalized = _uuid(command_id, "command_id")
        return next((item for item in self._records if item.command_id == normalized), None)

    def latest(self) -> ProjectOSUserManagementCommandRecord | None:
        self._align_runtime_generation()
        return self._records[-1] if self._records else None

    def undo_candidate(self) -> ProjectOSUserManagementCommandRecord | None:
        latest = self.latest()
        if latest is None:
            return None
        if latest.history_action not in {"command", "redo"}:
            return None
        return latest if latest.reversible else None

    def redo_candidate(self) -> ProjectOSUserManagementCommandRecord | None:
        latest = self.latest()
        if latest is None or latest.history_action != "undo" or not latest.reversible:
            return None
        return latest

    def state(self) -> dict[str, Any]:
        latest = self.latest()
        return {
            "count": len(self._records),
            "latest_command_id": latest.command_id if latest is not None else None,
            "latest_operation": latest.operation if latest is not None else None,
            "latest_reversible": latest.reversible if latest is not None else False,
            "can_undo": self.undo_candidate() is not None,
            "can_redo": self.redo_candidate() is not None,
            "persisted": False,
            "read_only": True,
        }

    def clear(self) -> None:
        self._records.clear()
        self._command_ids.clear()
        if self._runtime_generation_provider is not None:
            self._runtime_generation = int(self._runtime_generation_provider())
