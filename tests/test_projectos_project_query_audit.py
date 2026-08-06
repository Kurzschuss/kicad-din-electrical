from datetime import datetime, timezone
import sqlite3

import pytest

from projectos.application import Query
from projectos.authorization import AuthorizationContext, AuthorizationResult
from projectos.identifiers import BusinessId, CorrelationId
from projectos.project_queries import ProjectQueryExecutionResult, QUERY_COMMAND_SEARCH
from projectos.project_query_audit import AuditedProjectQueryPipeline
from projectos.project_query_authorization import AuthorizedProjectQueryResult
from projectos.results import MessageSeverity, Result, ResultMessage
from projectos.sqlite_audit import SQLiteAuditRepository


class StubAuthorizedPipeline:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def execute(self, query, *, context):
        self.calls += 1
        return self.result


def _query() -> Query:
    return Query(
        query_id=BusinessId("QRY-0059-0001"),
        query_type=QUERY_COMMAND_SEARCH,
        correlation_id=CorrelationId.from_sequence(59),
        requested_at=datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc),
        parameters={"project_id": "PRJ-0001"},
    )


def _context() -> AuthorizationContext:
    return AuthorizationContext(
        user_id=BusinessId("USR-0001"),
        role_ids=frozenset({BusinessId("ROLE-READER")}),
        project_id=BusinessId("PRJ-0001"),
    )


def _audit_repository():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    return connection, SQLiteAuditRepository(connection)


def test_erfolgreicher_query_zugriff_wird_persistent_auditiert():
    query = _query()
    authorized = AuthorizedProjectQueryResult(
        authorization=AuthorizationResult(True, "Rolle erlaubt."),
        execution=ProjectQueryExecutionResult(query, {"items": []}),
        permission=BusinessId("PERM-PROJECT-COMMAND-SEARCH"),
    )
    stub = StubAuthorizedPipeline(Result.success(authorized, correlation_id=query.correlation_id))
    connection, audit = _audit_repository()
    pipeline = AuditedProjectQueryPipeline(stub, audit)

    result = pipeline.execute(
        query,
        context=_context(),
        acting_role=BusinessId("ROLE-READER"),
        audit_id=BusinessId("AUD-QRY-0001"),
        reason="Diagnose für Projektprüfung.",
    )

    assert result.is_success
    assert stub.calls == 1
    entries = audit.all()
    assert len(entries) == 1
    assert entries[0].action == "project_query_accessed"
    assert entries[0].new_values["allowed"] is True
    assert audit.verify_integrity()
    connection.close()


def test_abgelehnter_query_zugriff_wird_ebenfalls_auditiert():
    query = _query()
    denied = Result.failure(
        ResultMessage(
            BusinessId("ERR-PRJ-QRY-0004"),
            MessageSeverity.ERROR,
            "Query nicht autorisiert.",
        ),
        correlation_id=query.correlation_id,
    )
    stub = StubAuthorizedPipeline(denied)
    connection, audit = _audit_repository()
    pipeline = AuditedProjectQueryPipeline(stub, audit)

    result = pipeline.execute(
        query,
        context=_context(),
        acting_role=BusinessId("ROLE-READER"),
        audit_id=BusinessId("AUD-QRY-0002"),
        reason="Abgelehnten Zugriff nachvollziehen.",
    )

    assert not result.is_success
    entry = audit.all()[0]
    assert entry.action == "project_query_denied"
    assert entry.new_values["allowed"] is False
    assert entry.new_values["message_codes"] == ["ERR-PRJ-QRY-0004"]
    assert audit.verify_integrity()
    connection.close()


def test_audit_kette_verknuepft_mehrere_query_zugriffe():
    query = _query()
    authorized = AuthorizedProjectQueryResult(
        AuthorizationResult(True, "Rolle erlaubt."),
        ProjectQueryExecutionResult(query, None),
        BusinessId("PERM-PROJECT-COMMAND-SEARCH"),
    )
    stub = StubAuthorizedPipeline(Result.success(authorized, correlation_id=query.correlation_id))
    connection, audit = _audit_repository()
    pipeline = AuditedProjectQueryPipeline(stub, audit)

    for number in (3, 4):
        pipeline.execute(
            query,
            context=_context(),
            acting_role=BusinessId("ROLE-READER"),
            audit_id=BusinessId(f"AUD-QRY-000{number}"),
            reason="Wiederholte Sicherheitsprüfung.",
        )

    first, second = audit.all()
    assert second.previous_hash == first.entry_hash
    assert audit.verify_integrity()
    connection.close()


def test_inaktive_handelnde_rolle_wird_vor_query_und_audit_abgelehnt():
    query = _query()
    stub = StubAuthorizedPipeline(Result.success(None, correlation_id=query.correlation_id))
    connection, audit = _audit_repository()
    pipeline = AuditedProjectQueryPipeline(stub, audit)

    with pytest.raises(PermissionError, match="ERR-AUTH-0002"):
        pipeline.execute(
            query,
            context=_context(),
            acting_role=BusinessId("ROLE-OTHER"),
            audit_id=BusinessId("AUD-QRY-0005"),
            reason="Nicht zulässig.",
        )

    assert stub.calls == 0
    assert audit.all() == ()
    connection.close()


def test_leere_begruendung_wird_abgelehnt():
    query = _query()
    stub = StubAuthorizedPipeline(Result.success(None, correlation_id=query.correlation_id))
    connection, audit = _audit_repository()
    pipeline = AuditedProjectQueryPipeline(stub, audit)

    with pytest.raises(ValueError, match="Begründung"):
        pipeline.execute(
            query,
            context=_context(),
            acting_role=BusinessId("ROLE-READER"),
            audit_id=BusinessId("AUD-QRY-0006"),
            reason="   ",
        )

    assert stub.calls == 0
    assert audit.all() == ()
    connection.close()
