from datetime import datetime, timezone

import pytest

from projectos import (
    BreakingCapacity,
    BusinessId,
    CorrelationId,
    DomainEvent,
    MCB,
    NominalCurrent,
    ObjectId,
    PoleCount,
    RatedVoltage,
    SQLiteOutboxRepository,
    SQLiteUnitOfWork,
    TripCharacteristic,
    add_with_outbox,
    create_mcb_sqlite_repository,
)


def make_mcb() -> MCB:
    return MCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("MCB-OUT-0001"),
        manufacturer="Test",
        product_name="B16",
        nominal_current=NominalCurrent(16),
        rated_voltage=RatedVoltage(230),
        trip_characteristic=TripCharacteristic.B,
        pole_count=PoleCount(1),
        breaking_capacity=BreakingCapacity(6000),
    )


def make_event(mcb: MCB, *, event_id: ObjectId | None = None) -> DomainEvent:
    return DomainEvent(
        event_id=ObjectId.new() if event_id is None else event_id,
        event_type="mcb.device.created",
        occurred_at=datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc),
        aggregate_id=mcb.object_id,
        aggregate_business_id=mcb.business_id,
        aggregate_revision=1,
        correlation_id=CorrelationId.from_sequence(41),
        payload={"manufacturer": mcb.manufacturer, "product_name": mcb.product_name},
    )


def test_geraet_und_ereignis_werden_atomar_persistiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()
    event = make_event(mcb)

    with SQLiteUnitOfWork(database) as uow:
        repository = create_mcb_sqlite_repository(uow.connection)
        outbox = SQLiteOutboxRepository(uow.connection)
        result = add_with_outbox(repository, outbox, mcb, event)
        assert result.is_success
        assert result.value is not None
        assert result.value.message.is_pending

    with SQLiteUnitOfWork(database) as uow:
        assert create_mcb_sqlite_repository(uow.connection).get(mcb.object_id) is not None
        pending = SQLiteOutboxRepository(uow.connection).pending()
        assert len(pending) == 1
        assert pending[0].event == event


def test_doppeltes_ereignis_rollt_geraetespeicherung_zurueck(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    first = make_mcb()
    shared_event_id = ObjectId.new()

    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        outbox.append(make_event(first, event_id=shared_event_id))

    second = MCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("MCB-OUT-0002"),
        manufacturer="Test",
        product_name="C16",
        nominal_current=NominalCurrent(16),
        rated_voltage=RatedVoltage(230),
        trip_characteristic=TripCharacteristic.C,
        pole_count=PoleCount(1),
        breaking_capacity=BreakingCapacity(6000),
    )
    with pytest.raises(ValueError):
        with SQLiteUnitOfWork(database) as uow:
            repository = create_mcb_sqlite_repository(uow.connection)
            outbox = SQLiteOutboxRepository(uow.connection)
            add_with_outbox(repository, outbox, second, make_event(second, event_id=shared_event_id))

    with SQLiteUnitOfWork(database) as uow:
        assert create_mcb_sqlite_repository(uow.connection).get(second.object_id) is None
        assert len(SQLiteOutboxRepository(uow.connection).all()) == 1


def test_ereignis_kann_als_veroeffentlicht_markiert_werden(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()
    event = make_event(mcb)

    with SQLiteUnitOfWork(database) as uow:
        outbox = SQLiteOutboxRepository(uow.connection)
        outbox.append(event)
        published = outbox.mark_published(
            event.event_id,
            published_at=datetime(2026, 8, 6, 8, 5, tzinfo=timezone.utc),
        )
        assert not published.is_pending
        assert published.attempts == 1
        assert outbox.pending() == ()


def test_pending_limit_muss_positiv_sein(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        with pytest.raises(ValueError):
            SQLiteOutboxRepository(uow.connection).pending(limit=0)
