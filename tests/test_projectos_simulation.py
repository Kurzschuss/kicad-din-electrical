from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    DomainEvent,
    ObjectId,
    SimulationClock,
    SimulationContext,
    SimulationTrace,
)


def test_simulation_clock_is_deterministic_and_advances() -> None:
    start = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
    clock = SimulationClock(start)

    assert clock.now_utc() == start
    assert clock.advance(timedelta(minutes=15)) == start + timedelta(minutes=15)


def test_simulation_clock_rejects_naive_and_backward_time() -> None:
    with pytest.raises(ValueError):
        SimulationClock(datetime(2026, 8, 6, 8, 0))

    clock = SimulationClock(datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc))
    with pytest.raises(ValueError):
        clock.advance(timedelta(seconds=-1))
    with pytest.raises(ValueError):
        clock.set(datetime(2026, 8, 6, 7, 59, tzinfo=timezone.utc))


def test_context_and_trace_are_stable() -> None:
    start = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
    context = SimulationContext(
        simulation_id=BusinessId("SIM-000001"),
        scenario_id=BusinessId("SCN-MCB-0001"),
        correlation_id=CorrelationId.from_sequence(1),
        started_at=start,
        metadata={"mode": "isolated"},
    )
    trace = SimulationTrace(context)

    first = trace.record(
        occurred_at=start,
        category="command",
        reference="mcb.component.validate",
        data={"value": 16},
    )
    second = trace.record(
        occurred_at=start + timedelta(seconds=1),
        category="result",
        reference="validation.success",
    )

    assert first.sequence == 1
    assert second.sequence == 2
    assert [entry.category for entry in trace.snapshot()] == ["COMMAND", "RESULT"]
    with pytest.raises(TypeError):
        first.data["value"] = 20
    with pytest.raises(FrozenInstanceError):
        first.sequence = 9


def test_domain_event_can_be_recorded() -> None:
    start = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
    context = SimulationContext(
        BusinessId("SIM-000002"),
        BusinessId("SCN-MCB-0002"),
        CorrelationId.from_sequence(2),
        start,
    )
    event = DomainEvent(
        event_id=ObjectId.new(),
        event_type="mcb.component.validated",
        occurred_at=start,
        aggregate_id=ObjectId.new(),
        aggregate_business_id=BusinessId("MCB-000001"),
        aggregate_revision=1,
        correlation_id=context.correlation_id,
        payload={"valid": True},
    )

    entry = SimulationTrace(context).record_event(event)

    assert entry.category == "EVENT"
    assert entry.reference == "mcb.component.validated"
    assert entry.data["payload"] == {"valid": True}
