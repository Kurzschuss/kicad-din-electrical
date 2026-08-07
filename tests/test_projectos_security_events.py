from dataclasses import replace
from datetime import datetime, timezone
import sqlite3
import pytest

from projectos.identifiers import BusinessId, CorrelationId
from projectos.security_events import (
    SecurityEvent,
    SecurityEventKind,
    SecurityEventSeverity,
    SecurityEventStatus,
    SQLiteSecurityEventRepository,
)

NOW = datetime(2026, 8, 6, 22, tzinfo=timezone.utc)


def _event(event_id: str = "SEV-00000001") -> SecurityEvent:
    return SecurityEvent(
        event_id=BusinessId(event_id),
        kind=SecurityEventKind.ALERT_ACTION_DENIED,
        severity=SecurityEventSeverity.WARNING,
        status=SecurityEventStatus.OPEN,
        occurred_at=NOW,
        source_type="SECURITY-ALERT",
        source_id=BusinessId("ALT-00000001"),
        actor_id=None,
        parent_event_id=None,
        correlation_id=CorrelationId("COR-01130001"),
        code="ERR-KICAD-0329",
        message="Autorisierung abgelehnt.",
        metadata={"action": "ACKNOWLEDGE"},
    )


def test_security_event_roundtrip_and_source_listing():
    repo = SQLiteSecurityEventRepository(sqlite3.connect(":memory:"))
    event = _event()
    assert repo.append(event) == event
    assert repo.list_for_source("SECURITY-ALERT", event.source_id) == (event,)


def test_security_event_requires_timezone_and_content():
    repo = SQLiteSecurityEventRepository(sqlite3.connect(":memory:"))
    invalid_time = replace(_event(), occurred_at=datetime(2026, 8, 6, 22))
    with pytest.raises(ValueError, match="ERR-KICAD-0337"):
        repo.append(invalid_time)


def test_security_event_id_is_unique():
    repo = SQLiteSecurityEventRepository(sqlite3.connect(":memory:"))
    event = _event()
    repo.append(event)
    with pytest.raises(ValueError, match="ERR-KICAD-0339"):
        repo.append(event)
