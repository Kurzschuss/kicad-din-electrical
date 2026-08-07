from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from projectos.audit import AuditEntry
from projectos.identifiers import BusinessId, CorrelationId, ObjectId
from projectos.query_audit_search import QueryAuditFilter, QueryAuditSearchService
from projectos.sqlite_audit import SQLiteAuditRepository


def _service():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    audit = SQLiteAuditRepository(connection)
    return connection, audit, QueryAuditSearchService(audit)


def _append(audit, number, *, allowed, actor="USR-0001", project="PRJ-0001", query_type="project.command.search"):
    previous_hash = audit.last_hash()
    audit.append(AuditEntry(
        audit_id=BusinessId(f"AUD-QRY-{number:04d}"),
        occurred_at=datetime(2026, 8, 6, 10, number, tzinfo=timezone.utc),
        actor_id=BusinessId(actor),
        acting_role=BusinessId("ROLE-READER"),
        permission_id=BusinessId("PERM-PROJECT-COMMAND-SEARCH"),
        object_id=ObjectId.new(),
        object_business_id=BusinessId(project),
        action="project_query_accessed" if allowed else "project_query_denied",
        reason="Diagnosezugriff.",
        correlation_id=CorrelationId.from_sequence(number),
        new_values={
            "query_id": f"QRY-{number:04d}",
            "query_type": query_type,
            "project_id": project,
            "allowed": allowed,
            "message_codes": [] if allowed else ["ERR-PRJ-QRY-0004"],
        },
        previous_hash=previous_hash,
    ))


def test_kombinierte_filter_und_neueste_sortierung():
    connection, audit, service = _service()
    _append(audit, 1, allowed=True)
    _append(audit, 2, allowed=False)
    _append(audit, 3, allowed=False, actor="USR-0002")

    page = service.search(QueryAuditFilter(
        project_id=BusinessId("PRJ-0001"),
        actor_id=BusinessId("USR-0001"),
        allowed=False,
    ))

    assert [str(item.audit_id) for item in page.items] == ["AUD-QRY-0002"]
    assert page.total_items == 1
    connection.close()


def test_pagination_und_statistik():
    connection, audit, service = _service()
    for number, allowed in ((1, True), (2, False), (3, True)):
        _append(audit, number, allowed=allowed)

    page = service.search(page=2, page_size=2)
    statistics = service.statistics()

    assert len(page.items) == 1
    assert page.has_previous is True
    assert page.has_next is False
    assert statistics.total == 3
    assert statistics.allowed == 2
    assert statistics.denied == 1
    assert statistics.denial_rate == pytest.approx(1 / 3)
    assert statistics.by_query_type == (("project.command.search", 3),)
    connection.close()


def test_zeitgrenzen_sind_einschliesslich():
    connection, audit, service = _service()
    _append(audit, 1, allowed=True)
    _append(audit, 2, allowed=True)
    instant = datetime(2026, 8, 6, 10, 1, tzinfo=timezone.utc)

    assert service.count(QueryAuditFilter(occurred_from=instant, occurred_until=instant)) == 1
    connection.close()


def test_unzulaessige_parameter_werden_abgelehnt():
    with pytest.raises(ValueError, match="ERR-PRJ-QRY-0008"):
        QueryAuditFilter(
            occurred_from=datetime(2026, 8, 6, 11, tzinfo=timezone.utc),
            occurred_until=datetime(2026, 8, 6, 10, tzinfo=timezone.utc),
        )

    connection, _, service = _service()
    with pytest.raises(ValueError, match="ERR-PRJ-QRY-0010"):
        service.search(page=0)
    with pytest.raises(ValueError, match="ERR-PRJ-QRY-0009"):
        service.search(page_size=201)
    connection.close()


def test_fremde_audit_aktionen_werden_ignoriert():
    connection, audit, service = _service()
    audit.append(AuditEntry(
        audit_id=BusinessId("AUD-OTHER-0001"),
        occurred_at=datetime.now(timezone.utc),
        actor_id=BusinessId("USR-0001"),
        acting_role=BusinessId("ROLE-READER"),
        permission_id=BusinessId("PERM-OTHER"),
        object_id=ObjectId.new(),
        object_business_id=BusinessId("OBJ-OTHER"),
        action="other_action",
        reason="Andere Aktion.",
        correlation_id=CorrelationId.from_sequence(999),
        previous_hash="",
    ))

    assert service.count() == 0
    connection.close()
