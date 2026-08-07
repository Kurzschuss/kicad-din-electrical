from datetime import datetime, timezone, timedelta
import pytest
from projectos import (
    AuthorizedGlobalSecurityStaffingReleaseAlertService, BusinessId, CorrelationId,
    GlobalSecurityResponsibility, GlobalSecurityResponsibilityType,
    GlobalSecurityStaffingReleaseAlertFinding, GlobalSecurityStaffingReleaseAlertLevel,
    GlobalSecurityStaffingReleaseAttemptAlertResult, Role,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_RESOLVE,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertRepository, SQLiteIdentityRepository,
    SQLiteUnitOfWork, UserAccount,
)
NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)
PRIMARY=BusinessId("USR-SECURITY"); DEPUTY=BusinessId("USR-SECURITY-DEPUTY")
ROLE=BusinessId("ROLE-SECURITY-ALERT"); WRONG=BusinessId("ROLE-OBSERVER")

def setup(uow, *, grant_ack=True, grant_resolve=True):
    identities=SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY,"Sicherheitsleitung")); identities.upsert_user(UserAccount(DEPUTY,"Vertretung"))
    perms=set()
    if grant_ack: perms.add(PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE)
    if grant_resolve: perms.add(PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_RESOLVE)
    identities.upsert_role(Role(ROLE,frozenset(perms))); identities.upsert_role(Role(WRONG,frozenset()))
    identities.assign_role(PRIMARY,ROLE); identities.assign_role(PRIMARY,WRONG); identities.assign_role(DEPUTY,ROLE)
    responsibilities=SQLiteGlobalSecurityResponsibilityRepository(uow.connection,identities)
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY,PRIMARY,NOW,"Hauptverantwortung"))
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY,DEPUTY,NOW,"Stellvertretung"))
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertRepository(uow.connection)
    result=GlobalSecurityStaffingReleaseAttemptAlertResult(NOW,NOW-timedelta(hours=24),3,1,GlobalSecurityStaffingReleaseAlertLevel.WARNING,(GlobalSecurityStaffingReleaseAlertFinding("WARN-KICAD-0005",GlobalSecurityStaffingReleaseAlertLevel.WARNING,"Warnung"),))
    alerts.create(alert_id=BusinessId("GSEC-ALERT-1001"),result=result,correlation_id=CorrelationId("COR-00002001"))
    audit=SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository(uow.connection)
    return AuthorizedGlobalSecurityStaffingReleaseAlertService(responsibilities,identities,alerts,audit),alerts,audit

def test_hauptverantwortung_bestaetigt_und_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,audit=setup(uow)
        result=service.acknowledge(BusinessId("GSEC-ALERT-1001"),action_id=BusinessId("GSEC-ACT-1001"),acknowledged_at=NOW,acting_role=ROLE,reason="Geprüft.",correlation_id=CorrelationId("COR-00002002"))
        assert result.alert.acknowledged_by==PRIMARY
        assert len(audit.list_for_alert(BusinessId("GSEC-ALERT-1001")))==1

def test_stellvertretung_kann_abschliessen(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,audit=setup(uow)
        service.acknowledge(BusinessId("GSEC-ALERT-1001"),action_id=BusinessId("GSEC-ACT-1002"),acknowledged_at=NOW,acting_role=ROLE,reason="Übernommen.",correlation_id=CorrelationId("COR-00002003"))
        result=service.resolve(BusinessId("GSEC-ALERT-1001"),action_id=BusinessId("GSEC-ACT-1003"),resolved_at=NOW+timedelta(minutes=1),acting_role=ROLE,reason="Abgeschlossen.",correlation_id=CorrelationId("COR-00002004"),unavailable_user_ids=frozenset({PRIMARY}))
        assert result.alert.resolved_by==DEPUTY
        assert len(audit.list_for_alert(BusinessId("GSEC-ALERT-1001")))==2

def test_falsche_rolle_veraendert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,audit=setup(uow)
        with pytest.raises(PermissionError,match="ERR-KICAD-0182"):
            service.acknowledge(BusinessId("GSEC-ALERT-1001"),action_id=BusinessId("GSEC-ACT-1004"),acknowledged_at=NOW,acting_role=WRONG,reason="Nein.",correlation_id=CorrelationId("COR-00002005"))
        assert alerts.get(BusinessId("GSEC-ALERT-1001")).status.value=="OPEN"
        assert audit.list_for_alert(BusinessId("GSEC-ALERT-1001"))==()

def test_fehlende_berechtigung_veraendert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,audit=setup(uow,grant_ack=False)
        with pytest.raises(PermissionError,match="ERR-KICAD-0181"):
            service.acknowledge(BusinessId("GSEC-ALERT-1001"),action_id=BusinessId("GSEC-ACT-1005"),acknowledged_at=NOW,acting_role=ROLE,reason="Nein.",correlation_id=CorrelationId("COR-00002006"))
        assert alerts.get(BusinessId("GSEC-ALERT-1001")).status.value=="OPEN"
        assert audit.list_for_alert(BusinessId("GSEC-ALERT-1001"))==()
