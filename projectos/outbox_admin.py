"""Administrative Diagnose und kontrollierte Dead-Letter-Wiederaufnahme."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .identifiers import BusinessId, ObjectId
from .outbox import SQLiteOutboxRepository
from .outbox_delivery import DeliveryState, DeliveryStatus, SQLiteDeliveryRepository


@dataclass(frozen=True, slots=True)
class OutboxDiagnostic:
    total_messages: int
    pending: int
    retry: int
    published: int
    dead_letter: int


@dataclass(frozen=True, slots=True)
class DeadLetterRecovery:
    event_id: ObjectId
    actor_id: BusinessId
    reason: str
    resumed_at: datetime
    state: DeliveryState

    def __post_init__(self) -> None:
        reason = self.reason.strip()
        if not reason:
            raise ValueError("Eine Wiederaufnahme benötigt eine Begründung.")
        if self.resumed_at.tzinfo is None:
            raise ValueError("resumed_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "resumed_at", self.resumed_at.astimezone(timezone.utc))


class OutboxAdministrationService:
    def __init__(self, outbox: SQLiteOutboxRepository, deliveries: SQLiteDeliveryRepository) -> None:
        self._outbox = outbox
        self._deliveries = deliveries

    def diagnose(self) -> OutboxDiagnostic:
        messages = self._outbox.all()
        states = {state.event_id: state for state in self._deliveries.all()}
        counts = {status: 0 for status in DeliveryStatus}
        for message in messages:
            state = states.get(message.event.event_id)
            if message.published_at is not None:
                counts[DeliveryStatus.PUBLISHED] += 1
            elif state is None:
                counts[DeliveryStatus.PENDING] += 1
            else:
                counts[state.status] += 1
        return OutboxDiagnostic(
            total_messages=len(messages),
            pending=counts[DeliveryStatus.PENDING],
            retry=counts[DeliveryStatus.RETRY],
            published=counts[DeliveryStatus.PUBLISHED],
            dead_letter=counts[DeliveryStatus.DEAD_LETTER],
        )

    def recover_dead_letter(
        self,
        event_id: ObjectId,
        *,
        actor_id: BusinessId,
        reason: str,
        resumed_at: datetime,
    ) -> DeadLetterRecovery:
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("Eine Wiederaufnahme benötigt eine Begründung.")
        if resumed_at.tzinfo is None:
            raise ValueError("resumed_at benötigt einen Zeitzonenbezug.")
        if not any(message.event.event_id == event_id for message in self._outbox.all()):
            raise LookupError("ERR-OUT-0004: Outbox-Nachricht wurde nicht gefunden.")
        instant = resumed_at.astimezone(timezone.utc)
        state = self._deliveries.resume_dead_letter(event_id, next_attempt_at=instant)
        return DeadLetterRecovery(event_id, actor_id, normalized_reason, instant, state)
