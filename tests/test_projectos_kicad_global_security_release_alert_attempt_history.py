from datetime import datetime, timezone, timedelta
import pytest
from projectos import BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertAttemptAlertFinding, GlobalSecurityStaffingReleaseAlertAttemptAlertLevel, GlobalSecurityStaffingReleaseAlertAttemptAlertResult, GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository, SQLiteUnitOfWork
NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)

def result(level=GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING):
    findings=() if level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CLEAR else (GlobalSecurityStaffingReleaseAlertAttemptAlertFinding("WARN-KICAD-0009",level,"Warnung"),)
    return GlobalSecurityStaffingReleaseAlertAttemptAlertResult(NOW,NOW-timedelta(hours=24),4,3,1,1,level,findings)

def test_lebenszyklus_und_roundtrip(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection); aid=BusinessId("GSEC-ACT-ALERT-1001")
        created=repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00003001")); assert created.status is GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus.OPEN
        acknowledged=repo.acknowledge(aid,acknowledged_at=NOW+timedelta(minutes=1),acknowledged_by=BusinessId("USR-SECURITY"),reason="Geprueft."); assert acknowledged.status is GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus.ACKNOWLEDGED
        resolved=repo.resolve(aid,resolved_at=NOW+timedelta(minutes=2),resolved_by=BusinessId("USR-SECURITY"),reason="Abgeschlossen."); assert resolved.status is GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus.RESOLVED
        assert resolved.acknowledge_attempts==3 and resolved.resolve_attempts==1 and resolved.attempts_without_actor==1

def test_clear_wird_nicht_gespeichert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection)
        with pytest.raises(ValueError,match="ERR-KICAD-0205"): repo.create(alert_id=BusinessId("GSEC-ACT-ALERT-1002"),result=result(GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CLEAR),correlation_id=CorrelationId("COR-00003002"))

def test_direkter_abschluss_wird_abgelehnt(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection); aid=BusinessId("GSEC-ACT-ALERT-1003")
        repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00003003"))
        with pytest.raises(ValueError,match="ERR-KICAD-0210"): repo.resolve(aid,resolved_at=NOW+timedelta(minutes=1),resolved_by=BusinessId("USR-SECURITY"),reason="Zu frueh.")

def test_zeitreihenfolge_und_begruendung(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection); aid=BusinessId("GSEC-ACT-ALERT-1004")
        repo.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00003004"))
        with pytest.raises(ValueError,match="ERR-KICAD-0209"): repo.acknowledge(aid,acknowledged_at=NOW-timedelta(seconds=1),acknowledged_by=BusinessId("USR-SECURITY"),reason="Nein")
        with pytest.raises(ValueError,match="ERR-KICAD-0214"): repo.acknowledge(aid,acknowledged_at=NOW,acknowledged_by=BusinessId("USR-SECURITY"),reason=" ")

def test_statuslisten_sind_getrennt_und_sortiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path/"p.db") as uow:
        repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository(uow.connection)
        for suffix in ("1005","1006"): repo.create(alert_id=BusinessId(f"GSEC-ACT-ALERT-{suffix}"),result=result(),correlation_id=CorrelationId(f"COR-0000{suffix}"))
        repo.acknowledge(BusinessId("GSEC-ACT-ALERT-1005"),acknowledged_at=NOW,acknowledged_by=BusinessId("USR-SECURITY"),reason="Geprueft")
        assert len(repo.list_for_status(GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus.OPEN))==1
        assert len(repo.list_for_status(GlobalSecurityStaffingReleaseAlertAttemptHistoryStatus.ACKNOWLEDGED))==1
