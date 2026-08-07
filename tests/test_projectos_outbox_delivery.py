from datetime import datetime, timedelta, timezone

from projectos import (
    BusinessId, CorrelationId, DomainEvent, ObjectId, OutboxProcessor,
    SQLiteDeliveryRepository, SQLiteOutboxRepository, SQLiteUnitOfWork,
    DeliveryStatus,
)


def event() -> DomainEvent:
    return DomainEvent(
        event_id=ObjectId.new(),
        event_type="mcb.component.created",
        occurred_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
        aggregate_id=ObjectId.new(),
        aggregate_business_id=BusinessId("MCB-OUT-0001"),
        aggregate_revision=1,
        correlation_id=CorrelationId.from_sequence(1),
        payload={"status": "created"},
    )


def test_erfolgreiche_zustellung_markiert_nachricht_als_veroeffentlicht(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    delivered = []
    message = event()
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        outbox.append(message)
        processor = OutboxProcessor(outbox, SQLiteDeliveryRepository(uow.connection), delivered.append)
        result = processor.process(now=datetime(2026, 8, 6, 1, tzinfo=timezone.utc))
        assert result.published == 1
        assert delivered == [message]
        assert outbox.pending() == ()


def test_fehler_wird_nach_sperrzeit_erneut_versucht(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    message = event()
    calls = 0

    def fail(_: DomainEvent) -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("nicht erreichbar")

    start = datetime(2026, 8, 6, 1, tzinfo=timezone.utc)
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        outbox.append(message)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        processor = OutboxProcessor(outbox, deliveries, fail, retry_delay=timedelta(minutes=5))
        assert processor.process(now=start).failed == 1
        assert processor.process(now=start + timedelta(minutes=4)).processed == 0
        assert processor.process(now=start + timedelta(minutes=5)).failed == 1
        assert calls == 2
        assert deliveries.get(message.event_id).attempts == 2


def test_maximale_versuche_fuehren_in_dead_letter(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    message = event()

    def fail(_: DomainEvent) -> None:
        raise ValueError("dauerhafter Fehler")

    start = datetime(2026, 8, 6, 1, tzinfo=timezone.utc)
    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        outbox.append(message)
        deliveries = SQLiteDeliveryRepository(uow.connection)
        processor = OutboxProcessor(
            outbox, deliveries, fail, max_attempts=2, retry_delay=timedelta(0)
        )
        processor.process(now=start)
        result = processor.process(now=start)
        state = deliveries.get(message.event_id)
        assert result.dead_lettered == 1
        assert state.status is DeliveryStatus.DEAD_LETTER
        assert state.attempts == 2
        assert "dauerhafter Fehler" in (state.last_error or "")
        assert len(deliveries.dead_letters()) == 1
        assert processor.process(now=start).processed == 0
