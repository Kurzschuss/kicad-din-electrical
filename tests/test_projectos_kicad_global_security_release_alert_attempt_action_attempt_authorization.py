from datetime import datetime, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.identity_persistence import SQLiteIdentityRepository
from projectos.kicad_global_security import GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_history import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_authorization import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_RESOLVE,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository,
)

NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)

def _setup():
    c=sqlite3.connect(":memory:")
    ids=SQLiteIdentityRepository(c); resp=SQLiteGlobalSecurityResponsibilityRepository(c)
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository(c)
    audit=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository(c)
    return c,ids,resp,alerts,audit

def test_permissions_are_separate():
    assert PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE != PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_RESOLVE

def test_audit_repository_rejects_missing_reason():
    c,_,_,_,audit=_setup()
    record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord(BusinessId("ACT-01010001"),BusinessId("ALT-01000001"),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE,NOW,BusinessId("USR-00000001"),BusinessId("ROL-00000001"),PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,GlobalSecurityResponsibilityType.PRIMARY,"",CorrelationId("COR-01010001"))
    with pytest.raises(ValueError,match="ERR-KICAD-0253"): audit.append(record)

def test_audit_roundtrip():
    c,_,_,_,audit=_setup()
    record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord(BusinessId("ACT-01010002"),BusinessId("ALT-01000002"),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.RESOLVE,NOW,BusinessId("USR-00000002"),BusinessId("ROL-00000002"),PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_RESOLVE,GlobalSecurityResponsibilityType.DEPUTY,"Bearbeitung abgeschlossen",CorrelationId("COR-01010002"))
    audit.append(record)
    assert audit.list_for_alert(record.alert_id)==(record,)

def test_duplicate_action_id_is_rejected():
    c,_,_,_,audit=_setup()
    record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord(BusinessId("ACT-01010003"),BusinessId("ALT-01000003"),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE,NOW,BusinessId("USR-00000003"),BusinessId("ROL-00000003"),PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,GlobalSecurityResponsibilityType.PRIMARY,"Geprüft",CorrelationId("COR-01010003"))
    audit.append(record)
    with pytest.raises(ValueError,match="ERR-KICAD-0254"): audit.append(record)
