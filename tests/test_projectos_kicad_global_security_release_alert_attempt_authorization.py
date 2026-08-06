from datetime import datetime, timezone, timedelta
import pytest
from projectos import (
    AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryService, BusinessId, CorrelationId,
    GlobalSecurityResponsibility, GlobalSecurityResponsibilityType,
    GlobalSecurityStaffingReleaseAlertAttemptAlertFinding, GlobalSecurityStaffingReleaseAlertAttemptAlertLevel,
    GlobalSecurityStaffingReleaseAlertAttemptAlertResult, Role,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACKNOWLEDGE,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_RESOLVE,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository, SQLiteIdentityRepository,
    SQLiteUnitOfWork, UserAccount,
)
NOW=datetime(2026,8,6,19,0,tzinfo=timezone.utc)
PRIMARY=BusinessId("USR-SECURITY"); DEPUTY=BusinessId("USR-SECURITY-DEPUTY")
ROLE=BusinessId("ROLE-SECURITY-ATTEMPT-ALERT"); WRONG=BusinessId("ROLE-OBSERVER")
ALERT=BusinessId("GSEC-ATTEMPT-ALERT-1001")

def setup(uow, *, grant_ack=True, grant_resolve=True):
    identities=SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY,"Sicherheitsleitung")); identities.upsert_user(UserAccount(DEPUTY,"Vertretung"))
    permissions=set()
    if grant_ack: permissions.add(PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACKNOWLEDGE)
    if grant_resolve: permissions.add(PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_RESOLVE)
    identities.upsert_role(Role(ROLE,frozenset(permissions))); identities.upsert_role(Role(WRONG,frozenset()))
    identities.assign_role(PRIMARY,ROLE); identities.assign_role(PRIMARY,WRONG); identities.assign_role(DEPUTY,ROLE)
    responsibilities=SQLiteGlobalSecurityResponsibilityRepository(uow.connection,identities)
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY,PRIMARY,NOW,"Hauptverantwortung"))
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY,DEPUTY,NOW,"Stellvertretung"))
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection)
    result=GlobalSecurityStaffingReleaseAlertAttemptAlertResult(NOW,NOW-timedelta(hours=24),4,3,1,1,GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING,(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding("WARN-KICAD-0009",GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING,"Warnung"),))
    alerts.create(alert_id=ALERT,result=result,correlation_id=CorrelationId("COR-00003001"))
    audit=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRepository(uow.connection)
    return AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryService(responsibilities,identities,alerts,audit),alerts,audit

def test_hauptverantwortung_bestaetigt_und_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,audit=setup(uow)
        result=service.acknowledge(ALERT,action_id=BusinessId("GSEC-ATTEMPT-ACT-1001"),acknowledged_at=NOW,acting_role=ROLE,reason="Geprueft.",correlation_id=CorrelationId("COR-00003002"))
        assert result.alert.acknowledged_by==PRIMARY
        assert len(audit.list_for_alert(ALERT))==1

def test_stellvertretung_kann_abschliessen(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,audit=setup(uow)
        service.acknowledge(ALERT,action_id=BusinessId("GSEC-ATTEMPT-ACT-1002"),acknowledged_at=NOW,acting_role=ROLE,reason="Uebernommen.",correlation_id=CorrelationId("COR-00003003"))
        result=service.resolve(ALERT,action_id=BusinessId("GSEC-ATTEMPT-ACT-1003"),resolved_at=NOW+timedelta(minutes=1),acting_role=ROLE,reason="Abgeschlossen.",correlation_id=CorrelationId("COR-00003004"),unavailable_user_ids=frozenset({PRIMARY}))
        assert result.alert.resolved_by==DEPUTY
        assert len(audit.list_for_alert(ALERT))==2

def test_falsche_rolle_veraendert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,audit=setup(uow)
        with pytest.raises(PermissionError,match="ERR-KICAD-0219"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ATTEMPT-ACT-1004"),acknowledged_at=NOW,acting_role=WRONG,reason="Nein.",correlation_id=CorrelationId("COR-00003005"))
        assert alerts.get(ALERT).status.value=="OPEN"
        assert audit.list_for_alert(ALERT)==()

def test_fehlende_berechtigung_veraendert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,audit=setup(uow,grant_ack=False)
        with pytest.raises(PermissionError,match="ERR-KICAD-0218"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ATTEMPT-ACT-1005"),acknowledged_at=NOW,acting_role=ROLE,reason="Nein.",correlation_id=CorrelationId("COR-00003006"))
        assert alerts.get(ALERT).status.value=="OPEN"
        assert audit.list_for_alert(ALERT)==()
