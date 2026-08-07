from datetime import datetime, timedelta, timezone
import pytest
from projectos import (
    BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertAction,
    GlobalSecurityStaffingReleaseAlertActionAttemptRecord,
    GlobalSecurityStaffingReleaseAlertAttemptAlertLevel,
    GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy,
    GlobalSecurityStaffingReleaseAlertAttemptAlertService,
    SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository, SQLiteUnitOfWork,
)
NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)
ROLE=BusinessId("ROLE-SECURITY-ALERT"); USER=BusinessId("USR-SECURITY")
PERM=BusinessId("PERM-SECURITY-ALERT")

def append(repo,n,*, action=GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE, actor=USER, role=ROLE, code="ERR-KICAD-0182", at=None):
    repo.append(GlobalSecurityStaffingReleaseAlertActionAttemptRecord(
        BusinessId(f"GSEC-TRY-{n:04d}"),BusinessId("GSEC-ALERT-1001"),action,at or NOW,actor,role,PERM,code,"Abgelehnt.",CorrelationId(f"COR-{n:08d}")))

def test_leere_historie_ist_clear(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        result=GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=NOW)
        assert result.level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CLEAR
        assert result.total_attempts==0

def test_warnung_ab_standard_gesamtgrenze(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        for n in range(1,4): append(repo,n,actor=BusinessId(f"USR-{n:04d}"))
        result=GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=NOW)
        assert result.level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING
        assert any(x.code=="WARN-KICAD-0009" for x in result.findings)

def test_kritische_benutzerschwelle_hat_vorrang(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        for n in range(1,6): append(repo,n)
        result=GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=NOW)
        assert result.level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL
        assert any(x.code=="ERR-KICAD-0199" and x.subject_id==USER for x in result.findings)

def test_getrennte_aktionsschwellen(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        append(repo,1,action=GlobalSecurityStaffingReleaseAlertAction.RESOLVE)
        append(repo,2,action=GlobalSecurityStaffingReleaseAlertAction.RESOLVE)
        policy=GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy(warning_attempts=10,critical_attempts=20,warning_per_actor=None,critical_per_actor=None,warning_without_actor=None,critical_without_actor=None,warning_resolve=2,critical_resolve=4)
        result=GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=NOW,policy=policy)
        assert result.resolve_attempts==2
        assert any(x.code=="WARN-KICAD-0013" for x in result.findings)

def test_zeitfenster_und_kritischer_code(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        append(repo,1,at=NOW-timedelta(days=2))
        append(repo,2,code="ERR-KICAD-0122")
        policy=GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy(warning_attempts=10,critical_attempts=20,warning_per_actor=None,critical_per_actor=None,warning_without_actor=None,critical_without_actor=None,critical_denial_codes=("err-kicad-0122",))
        result=GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=NOW,policy=policy)
        assert result.total_attempts==1
        assert result.level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL
        assert any(x.code=="ERR-KICAD-0204" for x in result.findings)

def test_ungueltige_richtlinien_und_zeitpunkt(tmp_path):
    with pytest.raises(ValueError,match="ERR-KICAD-0193"):
        GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy(window=timedelta(0))
    with pytest.raises(ValueError,match="ERR-KICAD-0196"):
        GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy(warning_per_role=3,critical_per_role=2)
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        with pytest.raises(ValueError,match="ERR-KICAD-0197"):
            GlobalSecurityStaffingReleaseAlertAttemptAlertService(uow.connection).evaluate(evaluated_at=datetime(2026,8,6,18,0))
