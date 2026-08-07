from datetime import datetime, timedelta, timezone
import pytest
from projectos import (
    BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertAttemptHistoryAction,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptDiagnostic,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchFilter,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository,
    SQLiteUnitOfWork,
)
NOW=datetime(2026,8,6,19,0,tzinfo=timezone.utc)
ROLE=BusinessId("ROLE-SECURITY"); PERM=BusinessId("PERM-SECURITY")

def add(repo,n,*,action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.ACKNOWLEDGE,actor=True,code="ERR-KICAD-0218",reason="Berechtigung fehlt"):
    return repo.append(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord(BusinessId(f"ATT-{n:04d}"),BusinessId(f"ALERT-{n%2}"),action,NOW+timedelta(minutes=n),BusinessId(f"USR-{n%2}") if actor else None,ROLE,PERM,code,reason,CorrelationId(f"COR-{n:08d}")))

def test_kombinierte_filter_und_freitext(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(uow.connection); add(repo,1); add(repo,2,action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.RESOLVE,code="ERR-KICAD-0219",reason="Rolle passt nicht")
        service=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService(uow.connection)
        page=service.search(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchFilter(action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.RESOLVE,denial_code="err-kicad-0219",reason_text="passt"))
        assert [str(x.attempt_id) for x in page.items]==["ATT-0002"]

def test_stabile_pagination_neueste_zuerst(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(uow.connection)
        for n in range(1,4): add(repo,n)
        service=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService(uow.connection)
        page=service.search(page=2,page_size=2)
        assert [str(x.attempt_id) for x in page.items]==["ATT-0001"] and page.total_items==3 and page.has_previous and not page.has_next

def test_diagnose_aggregiert_aktionen_und_fehlende_person(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(uow.connection); add(repo,1); add(repo,2,action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.RESOLVE,actor=False); add(repo,3,code="ERR-KICAD-0219")
        d=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService(uow.connection).diagnostic()
        assert isinstance(d,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptDiagnostic)
        assert (d.total_attempts,d.acknowledge_attempts,d.resolve_attempts,d.attempts_without_actor)==(3,2,1,1)
        assert d.top_denial_codes[0]==("ERR-KICAD-0218",2)

def test_leere_diagnose(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(uow.connection)
        d=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService(uow.connection).diagnostic()
        assert d.total_attempts==0 and d.first_attempt_at is None and d.latest_attempt_at is None

def test_ungueltige_parameter(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(uow.connection); service=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchService(uow.connection)
        with pytest.raises(ValueError,match="ERR-KICAD-0228"): service.search(page=0)
        with pytest.raises(ValueError,match="ERR-KICAD-0229"): service.search(page_size=201)
        with pytest.raises(ValueError,match="ERR-KICAD-0226"): GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchFilter(from_timestamp=datetime(2026,8,6))
        with pytest.raises(ValueError,match="ERR-KICAD-0227"): GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptSearchFilter(from_timestamp=NOW,until_timestamp=NOW-timedelta(seconds=1))
