from datetime import datetime, timezone

import pytest

from projectos.application import Query
from projectos.identifiers import BusinessId, CorrelationId
from projectos.project_command_admin import CommandExecutionDiagnostic
from projectos.project_command_lifecycle import CommandLifecycleState, CommandLifecycleView
from projectos.project_command_search import CommandSearchPage
from projectos.project_queries import (
    QUERY_COMMAND_DIAGNOSTIC,
    QUERY_COMMAND_LIFECYCLE,
    QUERY_COMMAND_SEARCH,
    CommandQueryHandlers,
    ProjectQueryPipeline,
)


class LifecycleStub:
    def __init__(self) -> None:
        self.requested = None

    def get(self, command_id):
        self.requested = command_id
        return CommandLifecycleView(
            command_id=command_id,
            archived_executions=(),
            current_execution=None,
            recoveries=(),
            retry_attempts=(),
            state=CommandLifecycleState.NOT_FOUND,
        )


class SearchStub:
    def __init__(self) -> None:
        self.call = None

    def search(self, filters, *, page, page_size):
        self.call = (filters, page, page_size)
        return CommandSearchPage((), page, page_size, 0, 0)


class AdministrationStub:
    def diagnostic(self):
        return CommandExecutionDiagnostic(total=3, succeeded=2, rejected=1)


def query(query_type, parameters=None):
    return Query(
        query_id=BusinessId("QRY-0001"),
        query_type=query_type,
        correlation_id=CorrelationId.from_sequence(57),
        requested_at=datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc),
        parameters=parameters or {},
    )


def configured_pipeline():
    lifecycle = LifecycleStub()
    search = SearchStub()
    pipeline = ProjectQueryPipeline()
    CommandQueryHandlers(lifecycle, search, AdministrationStub()).register(pipeline)
    return pipeline, lifecycle, search


def test_lifecycle_query_uses_required_command_id():
    pipeline, lifecycle, _ = configured_pipeline()

    result = pipeline.execute(query(QUERY_COMMAND_LIFECYCLE, {"command_id": "CMD-0001"}))

    assert result.is_success
    assert result.value.value.state is CommandLifecycleState.NOT_FOUND
    assert lifecycle.requested == BusinessId("CMD-0001")


def test_search_query_maps_filters_and_pagination():
    pipeline, _, search = configured_pipeline()

    result = pipeline.execute(query(QUERY_COMMAND_SEARCH, {
        "project_id": "PRJ-0001",
        "command_type": "project.setting.change",
        "state": "succeeded",
        "processed_from": "2026-08-01T00:00:00+00:00",
        "text": "setting",
        "page": 2,
        "page_size": 25,
    }))

    assert result.is_success
    filters, page, page_size = search.call
    assert filters.project_id == BusinessId("PRJ-0001")
    assert filters.state is CommandLifecycleState.SUCCEEDED
    assert page == 2
    assert page_size == 25


def test_diagnostic_query_returns_summary():
    pipeline, _, _ = configured_pipeline()

    result = pipeline.execute(query(QUERY_COMMAND_DIAGNOSTIC))

    assert result.is_success
    assert result.value.value == CommandExecutionDiagnostic(3, 2, 1)


def test_unknown_query_type_returns_structured_failure():
    pipeline = ProjectQueryPipeline()

    result = pipeline.execute(query("project.command.unknown"))

    assert not result.is_success
    assert str(result.messages[0].code) == "ERR-PRJ-QRY-0001"


def test_missing_required_parameter_returns_structured_failure():
    pipeline, _, _ = configured_pipeline()

    result = pipeline.execute(query(QUERY_COMMAND_LIFECYCLE))

    assert not result.is_success
    assert str(result.messages[0].code) == "ERR-PRJ-QRY-0002"


def test_invalid_page_type_returns_structured_failure():
    pipeline, _, _ = configured_pipeline()

    result = pipeline.execute(query(QUERY_COMMAND_SEARCH, {"page": "2"}))

    assert not result.is_success
    assert str(result.messages[0].code) == "ERR-PRJ-QRY-0002"


def test_duplicate_query_registration_is_rejected():
    pipeline = ProjectQueryPipeline()
    pipeline.register(QUERY_COMMAND_DIAGNOSTIC, lambda _: None)

    with pytest.raises(ValueError, match="bereits"):
        pipeline.register(QUERY_COMMAND_DIAGNOSTIC, lambda _: None)
