"""Persistente SQLite-Outbox für atomar gespeicherte Domänenereignisse."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3
from types import MappingProxyType
from typing import Generic, Mapping, TypeVar

from .events import DomainEvent
from .identifiers import BusinessId, CorrelationId, ObjectId
from .repositories import RepositoryRecord
from .results import Result
from .sqlite import SQLiteJsonRepository

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class OutboxMessage:
    event: DomainEvent
    published_at: datetime | None = None
    attempts: int = 0

    def __post_init__(self) -> None:
        if self.attempts < 0:
            raise ValueError("Die Anzahl der Zustellversuche darf nicht negativ sein.")
        if self.published_at is not None:
            if self.published_at.tzinfo is None:
                raise ValueError("published_at benötigt einen Zeitzonenbezug.")
            object.__setattr__(self, "published_at", self.published_at.astimezone(timezone.utc))

    @property
    def is_pending(self) -> bool:
        return self.published_at is None


class SQLiteOutboxRepository:
    """Append-only-Outbox mit expliziter Zustellmarkierung."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_outbox (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                aggregate_business_id TEXT NOT NULL,
                aggregate_revision INTEGER NOT NULL,
                correlation_id TEXT,
                payload TEXT NOT NULL,
                published_at TEXT,
                attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0)
            )
            """
        )

    def append(self, event: DomainEvent) -> OutboxMessage:
        try:
            self._connection.execute(
                """
                INSERT INTO projectos_outbox(
                    event_id, event_type, occurred_at, aggregate_id,
                    aggregate_business_id, aggregate_revision, correlation_id, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.event_id),
                    event.event_type,
                    event.occurred_at.isoformat(),
                    str(event.aggregate_id),
                    str(event.aggregate_business_id),
                    event.aggregate_revision,
                    None if event.correlation_id is None else str(event.correlation_id),
                    json.dumps(dict(event.payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-OUT-0001: Ereignis ist bereits in der Outbox vorhanden.") from exc
        return OutboxMessage(event)

    def pending(self, *, limit: int = 100) -> tuple[OutboxMessage, ...]:
        if limit < 1:
            raise ValueError("Das Outbox-Limit muss mindestens 1 sein.")
        rows = self._connection.execute(
            "SELECT * FROM projectos_outbox WHERE published_at IS NULL ORDER BY rowid LIMIT ?",
            (limit,),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def mark_published(self, event_id: ObjectId, *, published_at: datetime) -> OutboxMessage:
        if published_at.tzinfo is None:
            raise ValueError("published_at benötigt einen Zeitzonenbezug.")
        instant = published_at.astimezone(timezone.utc)
        cursor = self._connection.execute(
            "UPDATE projectos_outbox SET published_at = ?, attempts = attempts + 1 WHERE event_id = ? AND published_at IS NULL",
            (instant.isoformat(), str(event_id)),
        )
        if cursor.rowcount == 0:
            raise LookupError("ERR-OUT-0002: Offenes Outbox-Ereignis wurde nicht gefunden.")
        row = self._connection.execute(
            "SELECT * FROM projectos_outbox WHERE event_id = ?", (str(event_id),)
        ).fetchone()
        assert row is not None
        return self._decode(row)

    def all(self) -> tuple[OutboxMessage, ...]:
        rows = self._connection.execute("SELECT * FROM projectos_outbox ORDER BY rowid").fetchall()
        return tuple(self._decode(row) for row in rows)

    @staticmethod
    def _decode(row: sqlite3.Row) -> OutboxMessage:
        raw_payload = json.loads(row["payload"])
        if not isinstance(raw_payload, dict):
            raise ValueError("Outbox-Payload muss ein JSON-Objekt sein.")
        event = DomainEvent(
            event_id=ObjectId.parse(row["event_id"]),
            event_type=row["event_type"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            aggregate_id=ObjectId.parse(row["aggregate_id"]),
            aggregate_business_id=BusinessId.parse(row["aggregate_business_id"]),
            aggregate_revision=int(row["aggregate_revision"]),
            correlation_id=(
                None if row["correlation_id"] is None else CorrelationId.parse(row["correlation_id"])
            ),
            payload=MappingProxyType(raw_payload),
        )
        published_at = None if row["published_at"] is None else datetime.fromisoformat(row["published_at"])
        return OutboxMessage(event=event, published_at=published_at, attempts=int(row["attempts"]))


@dataclass(frozen=True, slots=True)
class AtomicOutboxResult(Generic[T]):
    record: RepositoryRecord[T]
    message: OutboxMessage


def add_with_outbox(
    repository: SQLiteJsonRepository[T],
    outbox: SQLiteOutboxRepository,
    entity: T,
    event: DomainEvent,
) -> Result[AtomicOutboxResult[T]]:
    """Speichert Entität und Ereignis innerhalb der umgebenden Unit of Work."""

    stored = repository.add(entity)
    if not stored.is_success:
        return Result.failure(*stored.errors, correlation_id=event.correlation_id)
    assert stored.value is not None
    message = outbox.append(event)
    return Result.success(
        AtomicOutboxResult(record=stored.value, message=message),
        correlation_id=event.correlation_id,
    )
