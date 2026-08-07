from datetime import datetime, timezone, timedelta
import pytest
from projectos import (
    AuthorizedGlobalSecurityStaffingReleaseAlertService, BusinessId, CorrelationId,
    GlobalSecurityResponsibility, GlobalSecurityResponsibilityType,
    GlobalSecurityStaffingReleaseAlertFinding, GlobalSecurityStaffingReleaseAlertLevel,
    GlobalSecurityStaffingReleaseAttemptAlertResult, Role,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository,
    SQLiteGlobalSecurityStaffingReleaseAlertRepository, SQLiteIdentityRepository,
    SQLiteUnitOfWork, UserAccount,
)
NOW=datetime(2026,8,6,18,30,tzinfo=timezone.utc)
PRIMARY=BusinessId("USR-SECURITY"); DEPUTY=BusinessId("USR-SECURITY-DEPUTY")
ROLE=BusinessId("ROLE-SECURITY-ALERT"); WRONG=BusinessId("ROLE-OBSERVER")
ALERT=BusinessId("GSEC-ALERT-2001")

def setup(uow, *, grant=True):
    identities=SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY,"Sicherheitsleitung")); identities.upsert_user(UserAccount(DEPUTY,"Vertretung"))
    identities.upsert_role(Role(ROLE,frozenset({PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE}) if grant else frozenset()))
    identities.upsert_role(Role(WRONG,frozenset())); identities.assign_role(PRIMARY,ROLE); identities.assign_role(PRIMARY,WRONG); identities.assign_role(DEPUTY,ROLE)
    responsibilities=SQLiteGlobalSecurityResponsibilityRepository(uow.connection,identities)
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY,PRIMARY,NOW,"Hauptverantwortung"))
    responsibilities.assign(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY,DEPUTY,NOW,"Stellvertretung"))
    alerts=SQLiteGlobalSecurityStaffingReleaseAlertRepository(uow.connection)
    result=GlobalSecurityStaffingReleaseAttemptAlertResult(NOW,NOW-timedelta(hours=24),3,1,GlobalSecurityStaffingReleaseAlertLevel.WARNING,(GlobalSecurityStaffingReleaseAlertFinding("WARN-KICAD-0005",GlobalSecurityStaffingReleaseAlertLevel.WARNING,"Warnung"),))
    alerts.create(alert_id=ALERT,result=result,correlation_id=CorrelationId("COR-00003001"))
    success=SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository(uow.connection)
    attempts=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
    return AuthorizedGlobalSecurityStaffingReleaseAlertService(responsibilities,identities,alerts,success,attempts),alerts,success,attempts

def test_falsche_rolle_wird_auditiert_ohne_statusaenderung(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,success,attempts=setup(uow)
        with pytest.raises(PermissionError,match="ERR-KICAD-0182"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ACT-2001"),attempt_id=BusinessId("GSEC-TRY-2001"),acknowledged_at=NOW,acting_role=WRONG,reason="Nicht berechtigt.",correlation_id=CorrelationId("COR-00003002"))
        assert alerts.get(ALERT).status.value=="OPEN"; assert success.list_for_alert(ALERT)==()
        assert attempts.list_for_alert(ALERT)[0].denial_code=="ERR-KICAD-0182"

def test_fehlende_berechtigung_wird_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,_,attempts=setup(uow,grant=False)
        with pytest.raises(PermissionError,match="ERR-KICAD-0181"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ACT-2002"),attempt_id=BusinessId("GSEC-TRY-2002"),acknowledged_at=NOW,acting_role=ROLE,reason="Nicht berechtigt.",correlation_id=CorrelationId("COR-00003003"))
        assert attempts.list_for_alert(ALERT)[0].actor_id==PRIMARY

def test_fehlende_verantwortung_wird_ohne_actor_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,alerts,success,attempts=setup(uow)
        with pytest.raises(LookupError,match="ERR-KICAD-0122"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ACT-2003"),attempt_id=BusinessId("GSEC-TRY-2003"),acknowledged_at=NOW,acting_role=ROLE,reason="Niemand verfügbar.",correlation_id=CorrelationId("COR-00003004"),unavailable_user_ids=frozenset({PRIMARY,DEPUTY}))
        assert attempts.list_for_alert(ALERT)[0].actor_id is None
        assert alerts.get(ALERT).status.value=="OPEN"; assert success.list_for_alert(ALERT)==()

def test_aktiviertes_audit_erfordert_versuchskennung(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        service,_,_,attempts=setup(uow)
        with pytest.raises(ValueError,match="ERR-KICAD-0188"):
            service.acknowledge(ALERT,action_id=BusinessId("GSEC-ACT-2004"),acknowledged_at=NOW,acting_role=WRONG,reason="Fehlt.",correlation_id=CorrelationId("COR-00003005"))
        assert attempts.list_for_alert(ALERT)==()
