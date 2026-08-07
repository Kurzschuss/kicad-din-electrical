from datetime import datetime, timedelta, timezone
import sqlite3, pytest
from projectos import (BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertFinding,
GlobalSecurityStaffingReleaseAlertLevel, GlobalSecurityStaffingReleaseAttemptAlertResult,
GlobalSecurityStaffingReleaseAlertStatus, SQLiteGlobalSecurityStaffingReleaseAlertRepository)
NOW=datetime(2026,8,6,18,30,tzinfo=timezone.utc)

def result(level=GlobalSecurityStaffingReleaseAlertLevel.WARNING):
    findings=() if level is GlobalSecurityStaffingReleaseAlertLevel.CLEAR else (GlobalSecurityStaffingReleaseAlertFinding("WARN-KICAD-0005",level,"Grenze erreicht"),)
    return GlobalSecurityStaffingReleaseAttemptAlertResult(NOW,NOW-timedelta(hours=24),3,1,level,findings)

def repo(): return SQLiteGlobalSecurityStaffingReleaseAlertRepository(sqlite3.connect(":memory:"))

def test_alarm_durchlaeuft_lebenszyklus():
    r=repo(); aid=BusinessId("GSEC-ALERT-0001")
    created=r.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00002001"))
    assert created.status is GlobalSecurityStaffingReleaseAlertStatus.OPEN
    acknowledged=r.acknowledge(aid,acknowledged_at=NOW+timedelta(minutes=1),acknowledged_by=BusinessId("USR-SECURITY"),reason="Geprüft")
    assert acknowledged.status is GlobalSecurityStaffingReleaseAlertStatus.ACKNOWLEDGED
    resolved=r.resolve(aid,resolved_at=NOW+timedelta(minutes=2),resolved_by=BusinessId("USR-SECURITY"),reason="Bearbeitet")
    assert resolved.status is GlobalSecurityStaffingReleaseAlertStatus.RESOLVED

def test_clear_wird_nicht_gespeichert():
    with pytest.raises(ValueError,match="ERR-KICAD-0168"): repo().create(alert_id=BusinessId("GSEC-ALERT-0002"),result=result(GlobalSecurityStaffingReleaseAlertLevel.CLEAR),correlation_id=CorrelationId("COR-00002002"))

def test_direkter_abschluss_wird_abgelehnt():
    r=repo(); aid=BusinessId("GSEC-ALERT-0003"); r.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00002003"))
    with pytest.raises(ValueError,match="ERR-KICAD-0173"): r.resolve(aid,resolved_at=NOW+timedelta(minutes=1),resolved_by=BusinessId("USR-SECURITY"),reason="Zu früh")

def test_zeitliche_reihenfolge_wird_geprueft():
    r=repo(); aid=BusinessId("GSEC-ALERT-0004"); r.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00002004"))
    with pytest.raises(ValueError,match="ERR-KICAD-0172"): r.acknowledge(aid,acknowledged_at=NOW-timedelta(seconds=1),acknowledged_by=BusinessId("USR-SECURITY"),reason="Zu früh")

def test_begruendung_ist_pflicht():
    r=repo(); aid=BusinessId("GSEC-ALERT-0005"); r.create(alert_id=aid,result=result(),correlation_id=CorrelationId("COR-00002005"))
    with pytest.raises(ValueError,match="ERR-KICAD-0177"): r.acknowledge(aid,acknowledged_at=NOW,acknowledged_by=BusinessId("USR-SECURITY"),reason=" ")

def test_statuslisten_bleiben_getrennt():
    r=repo(); a=BusinessId("GSEC-ALERT-0006"); b=BusinessId("GSEC-ALERT-0007")
    r.create(alert_id=a,result=result(),correlation_id=CorrelationId("COR-00002006")); r.create(alert_id=b,result=result(),correlation_id=CorrelationId("COR-00002007")); r.acknowledge(b,acknowledged_at=NOW,acknowledged_by=BusinessId("USR-SECURITY"),reason="Übernommen")
    assert tuple(x.alert_id for x in r.list_for_status(GlobalSecurityStaffingReleaseAlertStatus.OPEN))==(a,)
    assert tuple(x.alert_id for x in r.list_for_status(GlobalSecurityStaffingReleaseAlertStatus.ACKNOWLEDGED))==(b,)
