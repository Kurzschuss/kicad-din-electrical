from datetime import datetime, timedelta, timezone
import sqlite3, pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertFinding as Finding,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertResult as Result,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_history import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryStatus as Status,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository as Repository,
)

def _result(level=Level.WARNING):
    now=datetime(2026,8,6,18,tzinfo=timezone.utc)
    findings=() if level is Level.CLEAR else (Finding("WARN-KICAD-0015",level,"Schwelle erreicht"),)
    return Result(now,now-timedelta(hours=24),3,2,1,0,level,findings)

def test_roundtrip_and_full_lifecycle():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0100-0001")
    created=repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-00000001"))
    assert created.status is Status.OPEN and created.acknowledge_attempts==2 and created.resolve_attempts==1
    acknowledged=repo.acknowledge(aid,acknowledged_at=created.created_at+timedelta(minutes=1),acknowledged_by=BusinessId("USER-0001"),reason="Geprueft")
    assert acknowledged.status is Status.ACKNOWLEDGED
    resolved=repo.resolve(aid,resolved_at=created.created_at+timedelta(minutes=2),resolved_by=BusinessId("USER-0002"),reason="Abgeschlossen")
    assert resolved.status is Status.RESOLVED

def test_clear_result_is_rejected():
    repo=Repository(sqlite3.connect(":memory:"))
    with pytest.raises(ValueError,match="ERR-KICAD-0242"):
        repo.create(alert_id=BusinessId("ALERT-0100-0002"),result=_result(Level.CLEAR),correlation_id=CorrelationId("COR-00000002"))

def test_direct_resolution_is_rejected():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0100-0003")
    record=repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-00000003"))
    with pytest.raises(ValueError,match="ERR-KICAD-0247"):
        repo.resolve(aid,resolved_at=record.created_at+timedelta(minutes=1),resolved_by=BusinessId("USER-0001"),reason="Zu frueh")

def test_action_reason_and_time_are_required():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0100-0004")
    record=repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-00000004"))
    with pytest.raises(ValueError,match="ERR-KICAD-0251"):
        repo.acknowledge(aid,acknowledged_at=record.created_at,acknowledged_by=BusinessId("USER-0001"),reason=" ")
    with pytest.raises(ValueError,match="ERR-KICAD-0250"):
        repo.acknowledge(aid,acknowledged_at=datetime(2026,8,6,18),acknowledged_by=BusinessId("USER-0001"),reason="Geprueft")

def test_status_lists_are_separated():
    repo=Repository(sqlite3.connect(":memory:"))
    first=repo.create(alert_id=BusinessId("ALERT-0100-0005"),result=_result(),correlation_id=CorrelationId("COR-00000005"))
    repo.create(alert_id=BusinessId("ALERT-0100-0006"),result=_result(),correlation_id=CorrelationId("COR-00000006"))
    repo.acknowledge(first.alert_id,acknowledged_at=first.created_at+timedelta(minutes=1),acknowledged_by=BusinessId("USER-0001"),reason="Geprueft")
    assert len(repo.list_for_status(Status.OPEN))==1
    assert len(repo.list_for_status(Status.ACKNOWLEDGED))==1
