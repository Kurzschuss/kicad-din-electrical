from datetime import datetime,timedelta,timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId,CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding as Finding,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertResult as Result,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_history import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus as Status,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository as Repository,
)
NOW=datetime(2026,8,6,22,tzinfo=timezone.utc)

def _result(level=Level.WARNING):
    findings=() if level is Level.CLEAR else (Finding("WARN-KICAD-0027",level,"Warnung"),)
    return Result(NOW,NOW-timedelta(hours=24),3,2,1,0,level,findings)

def test_roundtrip_and_status_lifecycle():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALT-01100001")
    created=repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-01100001"))
    assert created.status is Status.OPEN and created.total_attempts==3
    acknowledged=repo.acknowledge(aid,acknowledged_at=NOW+timedelta(minutes=1),acknowledged_by=BusinessId("USR-00000001"),reason="Geprueft")
    assert acknowledged.status is Status.ACKNOWLEDGED
    resolved=repo.resolve(aid,resolved_at=NOW+timedelta(minutes=2),resolved_by=BusinessId("USR-00000002"),reason="Abgeschlossen")
    assert resolved.status is Status.RESOLVED

def test_clear_cannot_be_persisted():
    repo=Repository(sqlite3.connect(":memory:"))
    with pytest.raises(ValueError,match="ERR-KICAD-0316"):
        repo.create(alert_id=BusinessId("ALT-01100002"),result=_result(Level.CLEAR),correlation_id=CorrelationId("COR-01100002"))

def test_resolve_requires_acknowledgement():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALT-01100003")
    repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-01100003"))
    with pytest.raises(ValueError,match="ERR-KICAD-0321"):
        repo.resolve(aid,resolved_at=NOW+timedelta(minutes=1),resolved_by=BusinessId("USR-00000003"),reason="Zu frueh")

def test_action_requires_timezone_and_reason():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALT-01100004")
    repo.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-01100004"))
    with pytest.raises(ValueError,match="ERR-KICAD-0324"):
        repo.acknowledge(aid,acknowledged_at=datetime(2026,8,6,22),acknowledged_by=BusinessId("USR-00000004"),reason="Geprueft")
    with pytest.raises(ValueError,match="ERR-KICAD-0325"):
        repo.acknowledge(aid,acknowledged_at=NOW,acknowledged_by=BusinessId("USR-00000004"),reason=" ")

def test_status_lists_are_separate():
    repo=Repository(sqlite3.connect(":memory:")); a=BusinessId("ALT-01100005"); b=BusinessId("ALT-01100006")
    repo.create(alert_id=a,result=_result(),correlation_id=CorrelationId("COR-01100005")); repo.create(alert_id=b,result=_result(),correlation_id=CorrelationId("COR-01100006"))
    repo.acknowledge(b,acknowledged_at=NOW,acknowledged_by=BusinessId("USR-00000005"),reason="Geprueft")
    assert tuple(x.alert_id for x in repo.list_for_status(Status.OPEN))==(a,)
    assert tuple(x.alert_id for x in repo.list_for_status(Status.ACKNOWLEDGED))==(b,)
