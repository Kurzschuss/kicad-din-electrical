from datetime import datetime,timedelta,timezone
import sqlite3,pytest
from projectos.identifiers import BusinessId,CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_alert import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding as Finding,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertResult as Result
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_history import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus as Status,SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository as Repository
NOW=datetime(2026,8,6,20,tzinfo=timezone.utc)
def result(level=Level.WARNING):
    findings=() if level is Level.CLEAR else (Finding("WARN-KICAD-0021",level,"Schwelle"),)
    return Result(NOW,NOW-timedelta(hours=24),3,2,1,0,level,findings)
def test_roundtrip_and_lifecycle():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0105-0001")
    record=repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-01050001")); assert record.status is Status.OPEN and record.acknowledge_attempts==2
    record=repo.acknowledge(aid,acknowledged_at=NOW+timedelta(minutes=1),acknowledged_by=BusinessId("USER-1"),reason="Geprueft"); assert record.status is Status.ACKNOWLEDGED
    record=repo.resolve(aid,resolved_at=NOW+timedelta(minutes=2),resolved_by=BusinessId("USER-2"),reason="Abgeschlossen"); assert record.status is Status.RESOLVED
def test_clear_is_rejected():
    repo=Repository(sqlite3.connect(":memory:"))
    with pytest.raises(ValueError,match="ERR-KICAD-0279"): repo.create(alert_id=BusinessId("ALERT-0105-0002"),result=result(Level.CLEAR),correlation_id=CorrelationId("COR-01050002"))
def test_direct_resolution_is_rejected():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0105-0003"); repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-01050003"))
    with pytest.raises(ValueError,match="ERR-KICAD-0284"): repo.resolve(aid,resolved_at=NOW+timedelta(minutes=1),resolved_by=BusinessId("USER-1"),reason="Nein")
def test_action_validation():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALERT-0105-0004"); repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-01050004"))
    with pytest.raises(ValueError,match="ERR-KICAD-0288"): repo.acknowledge(aid,acknowledged_at=NOW,acknowledged_by=BusinessId("USER-1"),reason=" ")
    with pytest.raises(ValueError,match="ERR-KICAD-0287"): repo.acknowledge(aid,acknowledged_at=datetime(2026,8,6,20),acknowledged_by=BusinessId("USER-1"),reason="Geprueft")
def test_status_lists_are_separated():
    repo=Repository(sqlite3.connect(":memory:")); first=repo.create(alert_id=BusinessId("ALERT-0105-0005"),result=result(),correlation_id=CorrelationId("COR-01050005")); repo.create(alert_id=BusinessId("ALERT-0105-0006"),result=result(),correlation_id=CorrelationId("COR-01050006")); repo.acknowledge(first.alert_id,acknowledged_at=NOW+timedelta(minutes=1),acknowledged_by=BusinessId("USER-1"),reason="Geprueft")
    assert len(repo.list_for_status(Status.OPEN))==1 and len(repo.list_for_status(Status.ACKNOWLEDGED))==1
