"""Wiederholbare Outbox-Verarbeitung mit Dead-Letter-Status."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import sqlite3

from .events import DomainEvent
from .identifiers import ObjectId
from .outbox import OutboxMessage, SQLiteOutboxRepository


class DeliveryStatus(StrEnum):
    PENDING = "PENDING"
    RETRY = "RETRY"
    PUBLISHED = "PUBLISHED"
    DEAD_LETTER = "DEAD_LETTER"


@dataclass(frozen=True, slots=True)
class DeliveryState:
    event_id: ObjectId
    status: DeliveryStatus
    attempts: int
    next_attempt_at: datetime | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        if self.attempts < 0:
            raise ValueError("Die Anzahl der Zustellversuche darf nicht negativ sein.")
        if self.next_attempt_at is not None:
            if self.next_attempt_at.tzinfo is None:
                raise ValueError("next_attempt_at benötigt einen Zeitzonenbezug.")
            object.__setattr__(self, "next_attempt_at", self.next_attempt_at.astimezone(timezone.utc))
        if self.last_error is not None:
            normalized = self.last_error.strip()
            object.__setattr__(self, "last_error", normalized or None)


@dataclass(frozen=True, slots=True)
class OutboxProcessingResult:
    processed: int
    published: int
    failed: int
    dead_lettered: int


Publisher = Callable[[DomainEvent], None]


class SQLiteDeliveryRepository:
    """Persistiert Zustellstatus getrennt von den unveränderlichen Outbox-Nutzdaten."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_outbox_delivery (
                event_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
                next_attempt_at TEXT,
                last_error TEXT
            )
            """
        )

    def get(self, event_id: ObjectId) -> DeliveryState:
        row = self._connection.execute(
            "SELECT * FROM projectos_outbox_delivery WHERE event_id = ?",
            (str(event_id),),
        ).fetchone()
        if row is None:
            return DeliveryState(event_id, DeliveryStatus.PENDING, 0)
        return self._decode(row)

    def due(self, messages: tuple[OutboxMessage, ...], *, now: datetime) -> tuple[OutboxMessage, ...]:
        if now.tzinfo is None:
            raise ValueError("now benötigt einen Zeitzonenbezug.")
        instant = now.astimezone(timezone.utc)
        due_messages: list[OutboxMessage] = []
        for message in messages:
            state = self.get(message.event.event_id)
            if state.status in {DeliveryStatus.PUBLISHED, DeliveryStatus.DEAD_LETTER}:
                continue
            if state.next_attempt_at is None or state.next_attempt_at <= instant:
                due_messages.append(message)
        return tuple(due_messages)

    def mark_published(self, event_id: ObjectId, *, attempts: int) -> DeliveryState:
        return self._write(
            DeliveryState(event_id, DeliveryStatus.PUBLISHED, attempts),
        )

    def mark_failure(
        self,
        event_id: ObjectId,
        *,
        attempts: int,
        error: str,
        next_attempt_at: datetime | None,
        dead_letter: bool,
    ) -> DeliveryState:
        status = DeliveryStatus.DEAD_LETTER if dead_letter else DeliveryStatus.RETRY
        return self._write(DeliveryState(event_id, status, attempts, next_attempt_at, error))

    def dead_letters(self) -> tuple[DeliveryState, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_outbox_delivery WHERE status = ? ORDER BY rowid",
            (DeliveryStatus.DEAD_LETTER.value,),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def _write(self, state: DeliveryState) -> DeliveryState:
        self._connection.execute(
            """
            INSERT INTO projectos_outbox_delivery(event_id, status, attempts, next_attempt_at, last_error)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                status = excluded.status,
                attempts = excluded.attempts,
                next_attempt_at = excluded.next_attempt_at,
                last_error = excluded.last_error
            """,
            (
                str(state.event_id),
                state.status.value,
                state.attempts,
                None if state.next_attempt_at is None else state.next_attempt_at.isoformat(),
                state.last_error,
            ),
        )
        return state

    @staticmethod
    def _decode(row: sqlite3.Row) -> DeliveryState:
        return DeliveryState(
            event_id=ObjectId.parse(row["event_id"]),
            status=DeliveryStatus(row["status"]),
            attempts=int(row["attempts"]),
            next_attempt_at=(
                None if row["next_attempt_at"] is None else datetime.fromisoformat(row["next_attempt_at"])
            ),
            last_error=row["last_error"],
        )


class OutboxProcessor:
    """Verarbeitet fällige Outbox-Nachrichten deterministisch und synchron."""

    def __init__(
        self,
        outbox: SQLiteOutboxRepository,
        deliveries: SQLiteDeliveryRepository,
        publisher: Publisher,
        *,
        max_attempts: int = 5,
        retry_delay: timedelta = timedelta(minutes=1),
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts muss mindestens 1 sein.")
        if retry_delay.total_seconds() < 0:
            raise ValueError("retry_delay darf nicht negativ sein.")
        self._outbox = outbox
        self._deliveries = deliveries
        self._publisher = publisher
        self._max_attempts = max_attempts
        self._retry_delay = retry_delay

    def process(self, *, now: datetime, limit: int = 100) -> OutboxProcessingResult:
        if now.tzinfo is None:
            raise ValueError("now benötigt einen Zeitzonenbezug.")
        instant = now.astimezone(timezone.utc)
        due = self._deliveries.due(self._outbox.pending(limit=limit), now=instant)
        published = failed = dead_lettered = 0
        for message in due:
            event_id = message.event.event_id
            attempts = self._deliveries.get(event_id).attempts + 1
            try:
                self._publisher(message.event)
            except Exception as exc:
                dead_letter = attempts >= self._max_attempts
                self._deliveries.mark_failure(
                    event_id,
                    attempts=attempts,
                    error=f"{type(exc).__name__}: {exc}",
                    next_attempt_at=None if dead_letter else instant + self._retry_delay,
                    dead_letter=dead_letter,
                )
                failed += 1
                dead_lettered += int(dead_letter)
                continue
            self._outbox.mark_published(event_id, published_at=instant)
            self._deliveries.mark_published(event_id, attempts=attempts)
            published += 1
        return OutboxProcessingResult(len(due), published, failed, dead_lettered)
