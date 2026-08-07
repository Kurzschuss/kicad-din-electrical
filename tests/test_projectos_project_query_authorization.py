"""Tests für projektbezogene Leseberechtigungen der Query-Pipeline."""

from datetime import datetime, timezone

from projectos.application import Query
from projectos.authorization import AuthorizationContext, AuthorizationService, Role
from projectos.identifiers import BusinessId, CorrelationId
from projectos.project_queries import (
    QUERY_COMMAND_DIAGNOSTIC,
    QUERY_COMMAND_LIFECYCLE,
    QUERY_COMMAND_SEARCH,
    ProjectQueryPipeline,
)
from projectos.project_query_authorization import (
    AuthorizedProjectQueryPipeline,
    PERM_PROJECT_COMMAND_DIAGNOSTIC_READ,
    PERM_PROJECT_COMMAND_LIFECYCLE_READ,
    PERM_PROJECT_COMMAND_SEARCH,
)

NOW = datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
OTHER_PROJECT = BusinessId("PRJ-0002")
USER = BusinessId("USR-0001")
ROLE = BusinessId("ROLE-READER")


def _query(query_type: str, parameters: dict[str, object] | None = None) -> Query:
    return Query(
        query_id=BusinessId("QRY-0001"),
        query_type=query_type,
        correlation_id=CorrelationId.from_sequence(1),
        requested_at=NOW,
        parameters=parameters or {},
    )


def _authorized_pipeline(*permissions: BusinessId) -> AuthorizedProjectQueryPipeline:
    pipeline = ProjectQueryPipeline()
    pipeline.register(QUERY_COMMAND_LIFECYCLE, lambda query: {"kind": "lifecycle"})
    pipeline.register(QUERY_COMMAND_SEARCH, lambda query: {"kind": "search"})
    pipeline.register(QUERY_COMMAND_DIAGNOSTIC, lambda query: {"kind": "diagnostic"})
    authorization = AuthorizationService(
        roles={ROLE: Role(ROLE, frozenset(permissions))},
    )
    return AuthorizedProjectQueryPipeline(authorization, pipeline)


def _context(project_id: BusinessId | None = PROJECT) -> AuthorizationContext:
    return AuthorizationContext(USER, frozenset({ROLE}), project_id)


def test_lifecycle_query_wird_mit_projektkontext_autorisiert() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_LIFECYCLE_READ)

    result = service.execute(
        _query(
            QUERY_COMMAND_LIFECYCLE,
            {"command_id": "CMD-0001", "project_id": PROJECT},
        ),
        context=_context(),
    )

    assert result.is_success
    assert result.value is not None
    assert result.value.permission == PERM_PROJECT_COMMAND_LIFECYCLE_READ
    assert result.value.execution.value == {"kind": "lifecycle"}


def test_suchquery_verwendet_eigene_leseberechtigung() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_SEARCH)

    result = service.execute(
        _query(QUERY_COMMAND_SEARCH, {"project_id": PROJECT}),
        context=_context(),
    )

    assert result.is_success
    assert result.value is not None
    assert result.value.permission == PERM_PROJECT_COMMAND_SEARCH


def test_diagnosequery_kann_ohne_projektkontext_autorisiert_werden() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_DIAGNOSTIC_READ)

    result = service.execute(
        _query(QUERY_COMMAND_DIAGNOSTIC),
        context=_context(None),
    )

    assert result.is_success


def test_fehlende_berechtigung_verhindert_handler_ausfuehrung() -> None:
    calls: list[str] = []
    pipeline = ProjectQueryPipeline()
    pipeline.register(QUERY_COMMAND_SEARCH, lambda query: calls.append(query.query_type))
    service = AuthorizedProjectQueryPipeline(AuthorizationService(), pipeline)

    result = service.execute(
        _query(QUERY_COMMAND_SEARCH, {"project_id": PROJECT}),
        context=_context(),
    )

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-PRJ-QRY-0004"
    assert calls == []


def test_fehlender_projektkontext_wird_vor_autorisierung_abgelehnt() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_SEARCH)

    result = service.execute(
        _query(QUERY_COMMAND_SEARCH, {"project_id": PROJECT}),
        context=_context(None),
    )

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-PRJ-QRY-0005"


def test_fehlender_projektparameter_wird_abgelehnt() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_SEARCH)

    result = service.execute(
        _query(QUERY_COMMAND_SEARCH),
        context=_context(),
    )

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-PRJ-QRY-0006"


def test_fremder_projektbereich_wird_abgelehnt() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_SEARCH)

    result = service.execute(
        _query(QUERY_COMMAND_SEARCH, {"project_id": OTHER_PROJECT}),
        context=_context(),
    )

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-PRJ-QRY-0007"


def test_nicht_konfigurierter_query_typ_wird_strukturiert_abgelehnt() -> None:
    service = _authorized_pipeline(PERM_PROJECT_COMMAND_SEARCH)

    result = service.execute(
        _query("project.unknown.read"),
        context=_context(),
    )

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-PRJ-QRY-0003"
