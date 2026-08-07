"""Persistenter SQLite-Audit-Trail und atomare Speicheroperationen."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from .audit import AuditEntry
from .identifiers import BusinessId, CorrelationId, ObjectId
from .repositories import RepositoryRecord
from .results import Result
from .sqlite import SQLiteJsonRepository

T = TypeVar("T")


class SQLiteAuditRepository:
    """Append-only-Audit-Speicher innerhalb einer bestehenden SQLite-Transaktion."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_audit (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT NOT NULL UNIQUE,
                occurred_at TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                acting_role TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                object_business_id TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                previous_values TEXT NOT NULL,
                new_values TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL UNIQUE
            )
            """
        )

    def append(self, entry: AuditEntry) -> AuditEntry:
        previous_hash = self.last_hash()
        if entry.previous_hash != previous_hash:
            raise ValueError("ERR-AUD-0002: Audit-Kette ist nicht konsistent.")
        try:
            self._connection.execute(
                """
                INSERT INTO projectos_audit(
                    audit_id, occurred_at, actor_id, acting_role, permission_id,
                    object_id, object_business_id, action, reason, correlation_id,
                    previous_values, new_values, previous_hash, entry_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(entry.audit_id), entry.occurred_at.isoformat(), str(entry.actor_id),
                    str(entry.acting_role), str(entry.permission_id), str(entry.object_id),
                    str(entry.object_business_id), entry.action, entry.reason,
                    str(entry.correlation_id), self._json(entry.previous_values),
                    self._json(entry.new_values), entry.previous_hash, entry.entry_hash,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-AUD-0001: Audit-Kennung oder Prüfsumme bereits vorhanden.") from exc
        return entry

    def all(self) -> tuple[AuditEntry, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_audit ORDER BY sequence"
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def by_object(self, object_id: ObjectId) -> tuple[AuditEntry, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_audit WHERE object_id = ? ORDER BY sequence",
            (str(object_id),),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def last_hash(self) -> str:
        row = self._connection.execute(
            "SELECT entry_hash FROM projectos_audit ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        return "" if row is None else str(row["entry_hash"])

    def verify_integrity(self) -> bool:
        previous_hash = ""
        for entry in self.all():
            if entry.previous_hash != previous_hash or entry.entry_hash != entry.calculate_hash():
                return False
            previous_hash = entry.entry_hash
        return True

    @staticmethod
    def _json(values) -> str:
        return json.dumps(dict(values), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)

    @staticmethod
    def _decode(row: sqlite3.Row) -> AuditEntry:
        return AuditEntry(
            audit_id=BusinessId(str(row["audit_id"])),
            occurred_at=datetime.fromisoformat(str(row["occurred_at"])),
            actor_id=BusinessId(str(row["actor_id"])),
            acting_role=BusinessId(str(row["acting_role"])),
            permission_id=BusinessId(str(row["permission_id"])),
            object_id=ObjectId.parse(str(row["object_id"])),
            object_business_id=BusinessId(str(row["object_business_id"])),
            action=str(row["action"]),
            reason=str(row["reason"]),
            correlation_id=CorrelationId.parse(str(row["correlation_id"])),
            previous_values=json.loads(str(row["previous_values"])),
            new_values=json.loads(str(row["new_values"])),
            previous_hash=str(row["previous_hash"]),
            entry_hash=str(row["entry_hash"]),
        )


@dataclass(frozen=True, slots=True)
class AtomicPersistenceResult(Generic[T]):
    record: RepositoryRecord[T]
    audit_entry: AuditEntry


def add_with_audit(
    repository: SQLiteJsonRepository[T],
    audit_repository: SQLiteAuditRepository,
    entity: T,
    audit_factory: Callable[[str], AuditEntry],
) -> Result[AtomicPersistenceResult[T]]:
    """Speichert Entität und Audit-Eintrag innerhalb derselben Unit of Work."""

    stored = repository.add(entity)
    if not stored.is_success:
        return Result.failure(*stored.errors, correlation_id=stored.correlation_id)
    assert stored.value is not None
    audit_entry = audit_factory(audit_repository.last_hash())
    audit_repository.append(audit_entry)
    return Result.success(
        AtomicPersistenceResult(stored.value, audit_entry),
        correlation_id=audit_entry.correlation_id,
    )
