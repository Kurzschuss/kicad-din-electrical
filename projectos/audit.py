"""Unveränderlicher, verketteter Audit-Trail für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Mapping

from .identifiers import BusinessId, CorrelationId, ObjectId


def _freeze(values: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(values))


def _canonical(values: Mapping[str, object]) -> str:
    return json.dumps(dict(values), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """Nicht veränderbarer Nachweis einer fachlich relevanten Änderung."""

    audit_id: BusinessId
    occurred_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    object_id: ObjectId
    object_business_id: BusinessId
    action: str
    reason: str
    correlation_id: CorrelationId
    previous_values: Mapping[str, object] = field(default_factory=dict)
    new_values: Mapping[str, object] = field(default_factory=dict)
    previous_hash: str = ""
    entry_hash: str = ""

    def __post_init__(self) -> None:
        action = self.action.strip()
        reason = self.reason.strip()
        if not action:
            raise ValueError("Die Audit-Aktion darf nicht leer sein.")
        if not reason:
            raise ValueError("Der Änderungsgrund darf nicht leer sein.")
        if self.occurred_at.tzinfo is None:
            raise ValueError("Der Audit-Zeitstempel benötigt einen Zeitzonenbezug.")
        occurred_at = self.occurred_at.astimezone(timezone.utc)
        previous_values = _freeze(self.previous_values)
        new_values = _freeze(self.new_values)
        object.__setattr__(self, "occurred_at", occurred_at)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "previous_values", previous_values)
        object.__setattr__(self, "new_values", new_values)
        expected_hash = self.calculate_hash()
        if self.entry_hash and self.entry_hash != expected_hash:
            raise ValueError("Die Prüfsumme des Audit-Eintrags ist ungültig.")
        object.__setattr__(self, "entry_hash", expected_hash)

    def calculate_hash(self) -> str:
        payload = {
            "audit_id": str(self.audit_id),
            "occurred_at": self.occurred_at.astimezone(timezone.utc).isoformat(),
            "actor_id": str(self.actor_id),
            "acting_role": str(self.acting_role),
            "permission_id": str(self.permission_id),
            "object_id": str(self.object_id),
            "object_business_id": str(self.object_business_id),
            "action": self.action.strip(),
            "reason": self.reason.strip(),
            "correlation_id": str(self.correlation_id),
            "previous_values": dict(self.previous_values),
            "new_values": dict(self.new_values),
            "previous_hash": self.previous_hash,
        }
        return sha256(_canonical(payload).encode("utf-8")).hexdigest()


class InMemoryAuditRepository:
    """Append-only-Referenzspeicher mit Integritätsprüfung."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._ids: set[BusinessId] = set()

    def append(self, entry: AuditEntry) -> AuditEntry:
        if entry.audit_id in self._ids:
            raise ValueError("ERR-AUD-0001: Audit-Kennung bereits vorhanden.")
        expected_previous_hash = self._entries[-1].entry_hash if self._entries else ""
        if entry.previous_hash != expected_previous_hash:
            raise ValueError("ERR-AUD-0002: Audit-Kette ist nicht konsistent.")
        self._entries.append(entry)
        self._ids.add(entry.audit_id)
        return entry

    def all(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    def by_object(self, object_id: ObjectId) -> tuple[AuditEntry, ...]:
        return tuple(entry for entry in self._entries if entry.object_id == object_id)

    def verify_integrity(self) -> bool:
        previous_hash = ""
        for entry in self._entries:
            if entry.previous_hash != previous_hash or entry.entry_hash != entry.calculate_hash():
                return False
            previous_hash = entry.entry_hash
        return True
