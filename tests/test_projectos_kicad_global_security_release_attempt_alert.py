from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from projectos import (
    BusinessId, CorrelationId, GlobalSecurityStaffingReleaseAlertLevel,
    GlobalSecurityStaffingReleaseAttemptAlertPolicy,
    GlobalSecurityStaffingReleaseAttemptAlertService,
    GlobalSecurityStaffingReleaseAttemptRecord,
    SQLiteGlobalSecurityStaffingReleaseAttemptRepository,
)
NOW=datetime(2026,8,6,18,0,tzinfo=timezone.utc)
ROLE=BusinessId("ROLE-SECURITY")
PERM=BusinessId("PERM-SECURITY")

def add(repo,n,actor=BusinessId("USR-SECURITY"),code="ERR-KICAD-0146"):
    for i in range(n):
        repo.append(GlobalSecurityStaffingReleaseAttemptRecord(BusinessId(f"ATT-{i:04d}"),NOW-timedelta(minutes=i),actor,ROLE,PERM,code,"abgelehnt",CorrelationId(f"COR-{i+1:08d}")))

def test_clear_ohne_versuche():
    c=sqlite3.connect(":memory:"); SQLiteGlobalSecurityStaffingReleaseAttemptRepository(c)
    assert GlobalSecurityStaffingReleaseAttemptAlertService(c).evaluate(evaluated_at=NOW).level is GlobalSecurityStaffingReleaseAlertLevel.CLEAR

def test_warnung_bei_drei_versuchen():
    c=sqlite3.connect(":memory:"); r=SQLiteGlobalSecurityStaffingReleaseAttemptRepository(c); add(r,3)
    result=GlobalSecurityStaffingReleaseAttemptAlertService(c).evaluate(evaluated_at=NOW)
    assert result.level is GlobalSecurityStaffingReleaseAlertLevel.WARNING

def test_kritisch_bei_fuenf_versuchen():
    c=sqlite3.connect(":memory:"); r=SQLiteGlobalSecurityStaffingReleaseAttemptRepository(c); add(r,5)
    assert GlobalSecurityStaffingReleaseAttemptAlertService(c).evaluate(evaluated_at=NOW).level is GlobalSecurityStaffingReleaseAlertLevel.CRITICAL

def test_versuche_ausserhalb_fenster_werden_ignoriert():
    c=sqlite3.connect(":memory:"); r=SQLiteGlobalSecurityStaffingReleaseAttemptRepository(c)
    r.append(GlobalSecurityStaffingReleaseAttemptRecord(BusinessId("ATT-OLD"),NOW-timedelta(days=2),BusinessId("USR-X"),ROLE,PERM,"ERR-X","alt",CorrelationId("COR-00000001")))
    assert GlobalSecurityStaffingReleaseAttemptAlertService(c).evaluate(evaluated_at=NOW).total_attempts==0

def test_kritischer_code_loest_aus():
    c=sqlite3.connect(":memory:"); r=SQLiteGlobalSecurityStaffingReleaseAttemptRepository(c); add(r,1,code="ERR-KICAD-0147")
    p=GlobalSecurityStaffingReleaseAttemptAlertPolicy(warning_attempts=10,critical_attempts=20,warning_per_actor=None,critical_per_actor=None,warning_without_actor=None,critical_without_actor=None,critical_denial_codes=("ERR-KICAD-0147",))
    assert GlobalSecurityStaffingReleaseAttemptAlertService(c).evaluate(evaluated_at=NOW,policy=p).level is GlobalSecurityStaffingReleaseAlertLevel.CRITICAL

def test_unzulaessige_richtlinie():
    with pytest.raises(ValueError,match="ERR-KICAD-0158"):
        GlobalSecurityStaffingReleaseAttemptAlertPolicy(window=timedelta(0))
