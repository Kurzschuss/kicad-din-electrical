from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security import GlobalSecurityResponsibilityType
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding as Finding,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertResult as Result,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_history import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_authorization import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord as AuditRecord,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE as ACK,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE as RES,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository as AuditRepository,
)
NOW=datetime(2026,8,6,22,tzinfo=timezone.utc)

def _result():
    return Result(NOW,NOW-timedelta(hours=24),3,2,1,0,Level.WARNING,(Finding("WARN-KICAD-0027",Level.WARNING,"Warnung"),))

def test_permissions_are_separate():
    assert ACK != RES

def test_audit_roundtrip():
    repo=AuditRepository(sqlite3.connect(":memory:"))
    record=AuditRecord(BusinessId("ACT-01110001"),BusinessId("ALT-01100001"),Action.ACKNOWLEDGE,NOW,BusinessId("USR-00000001"),BusinessId("ROL-00000001"),ACK,GlobalSecurityResponsibilityType.PRIMARY,"Geprueft",CorrelationId("COR-01110001"))
    repo.append(record)
    assert repo.list_for_alert(record.alert_id)==(record,)

def test_audit_requires_reason_timezone_and_unique_action_id():
    repo=AuditRepository(sqlite3.connect(":memory:"))
    blank=AuditRecord(BusinessId("ACT-01110002"),BusinessId("ALT-01100002"),Action.RESOLVE,NOW,BusinessId("USR-00000002"),BusinessId("ROL-00000002"),RES,GlobalSecurityResponsibilityType.DEPUTY," ",CorrelationId("COR-01110002"))
    with pytest.raises(ValueError,match="ERR-KICAD-0327"):
        repo.append(blank)
    naive=AuditRecord(blank.action_id,blank.alert_id,blank.action,NOW.replace(tzinfo=None),blank.actor_id,blank.acting_role,blank.permission_id,blank.responsibility,"Abgeschlossen",blank.correlation_id)
    with pytest.raises(ValueError,match="ERR-KICAD-0326"):
        repo.append(naive)
    valid=AuditRecord(blank.action_id,blank.alert_id,blank.action,NOW,blank.actor_id,blank.acting_role,blank.permission_id,blank.responsibility,"Abgeschlossen",blank.correlation_id)
    repo.append(valid)
    with pytest.raises(ValueError,match="ERR-KICAD-0328"):
        repo.append(valid)

def test_alert_remains_open_without_authorized_service_call():
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository(sqlite3.connect(":memory:"))
    aid=BusinessId("ALT-01100003")
    alerts.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-01110003"))
    assert alerts.get(aid).status.value=="OPEN"
