from datetime import datetime, timezone

import pytest

from projectos.application import Command, LocalCommandBus, LocalQueryBus, Query
from projectos.identifiers import BusinessId, CorrelationId
from projectos.results import Result


def make_command() -> Command:
    return Command(
        command_id=BusinessId("CMD-0001"),
        command_type="mcb.component.create",
        correlation_id=CorrelationId.from_sequence(1),
        issued_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
        payload={"name": "B16"},
        expected_revision=0,
    )


def make_query() -> Query:
    return Query(
        query_id=BusinessId("QRY-0001"),
        query_type="mcb.component.get",
        correlation_id=CorrelationId.from_sequence(2),
        requested_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
        parameters={"id": "MCB-0001"},
    )


def test_command_is_normalized_and_payload_is_read_only() -> None:
    command = make_command()
    assert command.command_type == "mcb.component.create"
    with pytest.raises(TypeError):
        command.payload["name"] = "C16"


def test_negative_expected_revision_is_rejected() -> None:
    with pytest.raises(ValueError):
        Command(
            BusinessId("CMD-0002"),
            "mcb.component.create",
            CorrelationId.from_sequence(3),
            expected_revision=-1,
        )


def test_command_bus_dispatches_registered_handler() -> None:
    bus = LocalCommandBus()
    bus.register("mcb.component.create", lambda command: Result.success(command.payload["name"]))
    result = bus.dispatch(make_command())
    assert result.is_success
    assert result.value == "B16"


def test_duplicate_command_handler_is_rejected() -> None:
    bus = LocalCommandBus()
    handler = lambda command: Result.success(None)
    bus.register("mcb.component.create", handler)
    with pytest.raises(ValueError):
        bus.register("mcb.component.create", handler)


def test_missing_command_handler_is_reported() -> None:
    with pytest.raises(LookupError):
        LocalCommandBus().dispatch(make_command())


def test_query_bus_executes_registered_handler() -> None:
    bus = LocalQueryBus()
    bus.register("mcb.component.get", lambda query: Result.success(query.parameters["id"]))
    result = bus.execute(make_query())
    assert result.is_success
    assert result.value == "MCB-0001"


def test_invalid_request_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        Query(
            BusinessId("QRY-0002"),
            "invalid",
            CorrelationId.from_sequence(4),
        )
