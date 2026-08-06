from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    DeliveryStatus,
    DomainEvent,
    ObjectId,
    OutboxAdministrationService,
    SQLiteDeliveryRepository,
    SQLiteOutboxRepository,
    SQLiteUnitOfWork,
)


def make_event() -> DomainEvent:
    return DomainEvent(
        event_id=ObjectId.new(),
        event_type="mcb.device.created",
        occurred_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
        aggregate_id=ObjectId.new(),
        aggregate_business_id=BusinessId("MCB-ADM-0001"),
        aggregate_revision=1,
        payload={"source": "test"},
    )


def test_diagnose_zaehlt_pending_retry_published_und_dead_letter(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        pending, retry, published, dead = (make_event() for _ in range(4))
        for event in (pending, retry, published, dead):
            outbox.append(event)
        deliveries.mark_failure(
            retry.event_id,
            attempts=1,
            error="temporär",
            next_attempt_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
            dead_letter=False,
        )
        outbox.mark_published(published.event_id, published_at=datetime(2026, 8, 6, tzinfo=timezone.utc))
        deliveries.mark_published(published.event_id, attempts=1)
        deliveries.mark_failure(
            dead.event_id,
            attempts=5,
            error="dauerhaft",
            next_attempt_at=None,
            dead_letter=True,
        )
        diagnostic = OutboxAdministrationService(outbox, deliveries).diagnose()
        assert diagnostic.total_messages == 4
        assert diagnostic.pending == 1
        assert diagnostic.retry == 1
        assert diagnostic.published == 1
        assert diagnostic.dead_letter == 1


def test_dead_letter_kann_begruendet_wiederaufgenommen_werden(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        event = make_event()
        outbox.append(event)
        deliveries.mark_failure(
            event.event_id,
            attempts=5,
            error="dauerhaft",
            next_attempt_at=None,
            dead_letter=True,
        )
        recovery = OutboxAdministrationService(outbox, deliveries).recover_dead_letter(
            event.event_id,
            actor_id=BusinessId("USR-ADMIN-0001"),
            reason="Externer Dienst ist wieder verfügbar.",
            resumed_at=datetime(2026, 8, 6, 10, tzinfo=timezone.utc),
        )
        assert recovery.state.status is DeliveryStatus.RETRY
        assert recovery.state.attempts == 0
        assert recovery.state.last_error is None


def test_wiederaufnahme_ohne_begruendung_wird_abgewiesen(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        event = make_event()
        outbox.append(event)
        deliveries.mark_failure(event.event_id, attempts=5, error="x", next_attempt_at=None, dead_letter=True)
        with pytest.raises(ValueError):
            OutboxAdministrationService(outbox, deliveries).recover_dead_letter(
                event.event_id,
                actor_id=BusinessId("USR-ADMIN-0001"),
                reason="   ",
                resumed_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
            )


def test_nur_dead_letter_darf_wiederaufgenommen_werden(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        event = make_event()
        outbox.append(event)
        with pytest.raises(ValueError):
            OutboxAdministrationService(outbox, deliveries).recover_dead_letter(
                event.event_id,
                actor_id=BusinessId("USR-ADMIN-0001"),
                reason="Manuelle Prüfung abgeschlossen.",
                resumed_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
            )
