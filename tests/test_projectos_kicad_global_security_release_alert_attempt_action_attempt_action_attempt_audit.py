from datetime import datetime, timedelta, timezone
import pytest
from projectos.authorization import Role
from projectos.identifiers import BusinessId, CorrelationId
from projectos.identity_persistence import SQLiteIdentityRepository, UserAccount
from projectos.kicad_global_security import GlobalSecurityResponsibility, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertFinding as Finding,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertResult as Result,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_history import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_authorization import (
    AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryService,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRepository
from projectos.sqlite import SQLiteUnitOfWork

NOW=datetime(2026,8,6,20,0,tzinfo=timezone.utc)
PRIMARY=BusinessId("USR-SECURITY"); DEPUTY=BusinessId("USR-DEPUTY")
ROLE=BusinessId("ROLE-SECURITY"); WRONG=BusinessId("ROLE-OBSERVER")
ALERT=BusinessId("ALERT-01020001")

def _setup(uow, *, grant=True):
    identities=SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY,"Sicherheitsleitung")); identities.upsert_user(UserAccount(DEPUTY,"Vertretung"))
    identities.upsert_role(Role(ROLE,frozenset({PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE}) if grant else frozenset()))
    identities.upsert_role(Role(WRONG,frozenset()))
    identities.assign_role(PRIMARY,ROLE); identities.assign_role(PRIMARY,WRONG); identities.assign_role(DEPUTY,ROLE)
    responsibilities=SQLiteGlobalSecurityResponsibilityRepository(uow.connection,identities)
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY,PRIMARY,NOW,"Hauptverantwortung"))
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY,DEPUTY,NOW,"Stellvertretung"))
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository(uow.connection)
    result=Result(NOW,NOW-timedelta(hours=24),3,2,1,0,Level.WARNING,(Finding("WARN-KICAD-0015",Level.WARNING,"Warnung"),))
    alerts.create(alert_id=ALERT,result=result,correlation_id=CorrelationId("COR-01020001"))
    success=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository(uow.connection)
    attempts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRepository(uow.connection)
    service=AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryService(responsibilities,identities,alerts,success,attempts)
    return service,alerts,success,attempts

def test_wrong_role_is_audited_without_state_change(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,success,attempts=_setup(uow)
        with pytest.raises(PermissionError,match="ERR-KICAD-0256"):
            service.acknowledge(ALERT,action_id=BusinessId("ACT-01020001"),attempt_id=BusinessId("TRY-01020001"),acknowledged_at=NOW,acting_role=WRONG,reason="Abgelehnt",correlation_id=CorrelationId("COR-01020002"))
        assert alerts.get(ALERT).status.value=="OPEN"
        assert success.list_for_alert(ALERT)==()
        assert attempts.list_for_alert(ALERT)[0].denial_code=="ERR-KICAD-0256"

def test_missing_permission_is_audited(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,success,attempts=_setup(uow,grant=False)
        with pytest.raises(PermissionError,match="ERR-KICAD-0255"):
            service.acknowledge(ALERT,action_id=BusinessId("ACT-01020002"),attempt_id=BusinessId("TRY-01020002"),acknowledged_at=NOW,acting_role=ROLE,reason="Abgelehnt",correlation_id=CorrelationId("COR-01020003"))
        assert alerts.get(ALERT).status.value=="OPEN" and success.list_for_alert(ALERT)==()
        assert len(attempts.list_for_alert(ALERT))==1

def test_enabled_attempt_audit_requires_attempt_id(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,_,attempts=_setup(uow)
        with pytest.raises(ValueError,match="ERR-KICAD-0262"):
            service.acknowledge(ALERT,action_id=BusinessId("ACT-01020003"),acknowledged_at=NOW,acting_role=ROLE,reason="Fehlt",correlation_id=CorrelationId("COR-01020004"))
        assert attempts.list_for_alert(ALERT)==()

def test_attempt_repository_rejects_duplicate_id(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,_,attempts=_setup(uow)
        for _ in range(2):
            with pytest.raises((PermissionError,ValueError)):
                service.acknowledge(ALERT,action_id=BusinessId("ACT-01020004"),attempt_id=BusinessId("TRY-01020004"),acknowledged_at=NOW,acting_role=WRONG,reason="Abgelehnt",correlation_id=CorrelationId("COR-01020005"))
        assert len(attempts.list_for_alert(ALERT))==1
