from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security import GlobalSecurityResponsibilityType
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding as Finding,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertResult as Result,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_history import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_authorization import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord as AuditRecord,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE as ACK,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE as RES,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository as AuditRepository,
)
NOW=datetime(2026,8,6,21,tzinfo=timezone.utc)

def _result():
    return Result(NOW,NOW-timedelta(hours=24),3,2,1,0,Level.WARNING,(Finding("WARN-KICAD-0021",Level.WARNING,"Warnung"),))

def test_permissions_are_separate():
    assert ACK != RES

def test_audit_roundtrip():
    repo=AuditRepository(sqlite3.connect(":memory:"))
    record=AuditRecord(BusinessId("ACT-01060001"),BusinessId("ALT-01050001"),Action.ACKNOWLEDGE,NOW,BusinessId("USR-00000001"),BusinessId("ROL-00000001"),ACK,GlobalSecurityResponsibilityType.PRIMARY,"Geprueft",CorrelationId("COR-01060001"))
    repo.append(record)
    assert repo.list_for_alert(record.alert_id)==(record,)

def test_audit_requires_reason_and_unique_action_id():
    repo=AuditRepository(sqlite3.connect(":memory:"))
    record=AuditRecord(BusinessId("ACT-01060002"),BusinessId("ALT-01050002"),Action.RESOLVE,NOW,BusinessId("USR-00000002"),BusinessId("ROL-00000002"),RES,GlobalSecurityResponsibilityType.DEPUTY," ",CorrelationId("COR-01060002"))
    with pytest.raises(ValueError,match="ERR-KICAD-0290"):
        repo.append(record)
    valid=AuditRecord(record.action_id,record.alert_id,record.action,record.occurred_at,record.actor_id,record.acting_role,record.permission_id,record.responsibility,"Abgeschlossen",record.correlation_id)
    repo.append(valid)
    with pytest.raises(ValueError,match="ERR-KICAD-0291"):
        repo.append(valid)

def test_alert_repository_remains_open_without_authorized_service_call():
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository(sqlite3.connect(":memory:"))
    aid=BusinessId("ALT-01050003")
    alerts.create(alert_id=aid,result=_result(),correlation_id=CorrelationId("COR-01060003"))
    assert alerts.get(aid).status.value=="OPEN"
