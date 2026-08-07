from datetime import datetime, timezone, timedelta
import pytest
from projectos import (
    BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertAction,
    GlobalSecurityStaffingReleaseAlertActionAttemptRecord,
    GlobalSecurityStaffingReleaseAlertAttemptSearchFilter,
    GlobalSecurityStaffingReleaseAlertAttemptSearchService,
    SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository, SQLiteUnitOfWork,
)
NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)

def add(repo, suffix, action, actor, role, code, minute):
    repo.append(GlobalSecurityStaffingReleaseAlertActionAttemptRecord(BusinessId(f"ATT-{suffix}"),BusinessId("ALERT-1"),action,NOW+timedelta(minutes=minute),BusinessId(actor) if actor else None,BusinessId(role),BusinessId("PERM-1"),code,"Berechtigung fehlt",CorrelationId(f"COR-{int(suffix):08d}")))

def test_kombinierte_filter_und_freitext(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        add(repo,"00000001",GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE,"USR-1","ROLE-A","ERR-A",0)
        add(repo,"00000002",GlobalSecurityStaffingReleaseAlertAction.RESOLVE,"USR-2","ROLE-B","ERR-B",1)
        service=GlobalSecurityStaffingReleaseAlertAttemptSearchService(uow.connection)
        page=service.search(GlobalSecurityStaffingReleaseAlertAttemptSearchFilter(action=GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE,acting_role=BusinessId("ROLE-A"),reason_text="fehlt"))
        assert page.total_items==1 and page.items[0].actor_id==BusinessId("USR-1")

def test_pagination_ist_stabil(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        for i in range(1,4): add(repo,f"{i:08d}",GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE,"USR-1","ROLE-A","ERR-A",i)
        service=GlobalSecurityStaffingReleaseAlertAttemptSearchService(uow.connection)
        page=service.search(page=2,page_size=2)
        assert page.total_items==3 and page.total_pages==2 and page.has_previous and not page.has_next

def test_diagnose_aggregiert_aktionen_und_fehlende_person(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        add(repo,"00000001",GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE,None,"ROLE-A","ERR-A",0)
        add(repo,"00000002",GlobalSecurityStaffingReleaseAlertAction.RESOLVE,"USR-2","ROLE-B","ERR-B",1)
        d=GlobalSecurityStaffingReleaseAlertAttemptSearchService(uow.connection).diagnostic()
        assert d.total_attempts==2 and d.attempts_without_actor==1 and d.acknowledge_attempts==1 and d.resolve_attempts==1

def test_leere_diagnose(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        d=GlobalSecurityStaffingReleaseAlertAttemptSearchService(uow.connection).diagnostic()
        assert d.total_attempts==0 and d.first_attempt_at is None

def test_ungueltige_parameter(tmp_path):
    with pytest.raises(ValueError,match="ERR-KICAD-0189"): GlobalSecurityStaffingReleaseAlertAttemptSearchFilter(from_timestamp=datetime(2026,8,6))
    with pytest.raises(ValueError,match="ERR-KICAD-0190"): GlobalSecurityStaffingReleaseAlertAttemptSearchFilter(from_timestamp=NOW,until_timestamp=NOW-timedelta(seconds=1))
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository(uow.connection)
        s=GlobalSecurityStaffingReleaseAlertAttemptSearchService(uow.connection)
        with pytest.raises(ValueError,match="ERR-KICAD-0191"): s.search(page=0)
        with pytest.raises(ValueError,match="ERR-KICAD-0192"): s.search(page_size=201)
