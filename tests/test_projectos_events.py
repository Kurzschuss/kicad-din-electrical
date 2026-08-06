from datetime import datetime, timedelta, timezone
from types import MappingProxyType

import pytest

from projectos import BusinessId, CorrelationId, DomainEvent, DomainEventCollector, LocalEventBus, ObjectId


def make_event(*, event_type: str = "mcb.component.created") -> DomainEvent:
    return DomainEvent(
        event_id=ObjectId.new(),
        event_type=event_type,
        occurred_at=datetime(2026, 8, 6, 6, 0, tzinfo=timezone(timedelta(hours=2))),
        aggregate_id=ObjectId.new(),
        aggregate_business_id=BusinessId("MCB-000123"),
        aggregate_revision=1,
        correlation_id=CorrelationId.from_sequence(45),
        payload={"status": "DRAFT"},
    )


def test_domain_event_normalisiert_zeit_auf_utc_und_schuetzt_payload() -> None:
    event = make_event()
    assert event.occurred_at == datetime(2026, 8, 6, 4, 0, tzinfo=timezone.utc)
    assert isinstance(event.payload, MappingProxyType)
    with pytest.raises(TypeError):
        event.payload["status"] = "RELEASED"  # type: ignore[index]


def test_ungueltiger_ereignistyp_wird_abgewiesen() -> None:
    with pytest.raises(ValueError):
        make_event(event_type="MCB Created")


def test_zeitpunkt_ohne_zeitzone_wird_abgewiesen() -> None:
    with pytest.raises(ValueError):
        DomainEvent(
            event_id=ObjectId.new(),
            event_type="mcb.component.created",
            occurred_at=datetime(2026, 8, 6, 6, 0),
            aggregate_id=ObjectId.new(),
            aggregate_business_id=BusinessId("MCB-000123"),
            aggregate_revision=0,
        )


def test_collector_erhaelt_reihenfolge_und_clear_gibt_snapshot_zurueck() -> None:
    collector = DomainEventCollector()
    first = make_event()
    second = make_event(event_type="mcb.component.validated")
    collector.add(first)
    collector.add(second)
    assert collector.pending == (first, second)
    assert collector.clear() == (first, second)
    assert collector.pending == ()


def test_collector_verhindert_doppelte_ereigniskennung() -> None:
    collector = DomainEventCollector()
    event = make_event()
    collector.add(event)
    with pytest.raises(ValueError):
        collector.add(event)


def test_event_bus_ruft_handler_deterministisch_auf() -> None:
    bus = LocalEventBus()
    calls: list[str] = []
    bus.subscribe("mcb.component.created", lambda event: calls.append("first"))
    bus.subscribe("mcb.component.created", lambda event: calls.append("second"))
    count = bus.publish(make_event())
    assert count == 2
    assert calls == ["first", "second"]


def test_event_bus_akzeptiert_ereignis_ohne_handler() -> None:
    assert LocalEventBus().publish(make_event()) == 0
