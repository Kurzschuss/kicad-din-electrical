from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_alert import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel, GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy, GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService
from projectos.kicad_global_security_release_alert_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryAction

UTC=timezone.utc

def _append(repo, suffix, at, *, actor=True, action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.ACKNOWLEDGE, code="ERR-X"):
    repo.append(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord(BusinessId(f"ATT-{suffix}"),BusinessId("ALT-1"),action,at,BusinessId("USR-1") if actor else None,BusinessId("ROL-1"),BusinessId("PERM-1"),code,"abgelehnt",CorrelationId("COR-00000001")))

def test_clear_without_attempts():
    c=sqlite3.connect(":memory:")
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(c)
    result=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService(c).evaluate(evaluated_at=datetime(2026,8,6,tzinfo=UTC))
    assert result.level is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel.CLEAR

def test_warning_and_critical_actor_threshold():
    c=sqlite3.connect(":memory:"); repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(c); now=datetime(2026,8,6,12,tzinfo=UTC)
    for i in range(3): _append(repo,str(i),now-timedelta(minutes=i))
    result=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService(c).evaluate(evaluated_at=now,policy=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy(warning_attempts=10,critical_attempts=20,warning_per_actor=2,critical_per_actor=3))
    assert result.level is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel.CRITICAL
    assert any(x.code=="ERR-KICAD-0236" for x in result.findings)

def test_action_and_without_actor_thresholds():
    c=sqlite3.connect(":memory:"); repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(c); now=datetime(2026,8,6,12,tzinfo=UTC)
    _append(repo,"1",now,actor=False,action=GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.RESOLVE)
    policy=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy(warning_attempts=10,critical_attempts=20,warning_per_actor=None,critical_per_actor=None,warning_resolve=1,critical_resolve=2,warning_without_actor=1,critical_without_actor=2)
    result=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService(c).evaluate(evaluated_at=now,policy=policy)
    assert result.level is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel.WARNING
    assert {x.code for x in result.findings}=={"WARN-KICAD-0019","WARN-KICAD-0020"}

def test_time_window_and_critical_code():
    c=sqlite3.connect(":memory:"); repo=SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRepository(c); now=datetime(2026,8,6,12,tzinfo=UTC)
    _append(repo,"old",now-timedelta(days=2),code="ERR-CRIT"); _append(repo,"new",now,code="ERR-CRIT")
    policy=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy(window=timedelta(hours=24),warning_attempts=10,critical_attempts=20,warning_per_actor=None,critical_per_actor=None,warning_without_actor=None,critical_without_actor=None,critical_denial_codes=("err-crit",))
    result=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService(c).evaluate(evaluated_at=now,policy=policy)
    assert result.total_attempts==1 and result.level is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertLevel.CRITICAL

def test_invalid_policy_and_naive_time():
    with pytest.raises(ValueError,match="ERR-KICAD-0230"): GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy(window=timedelta(0))
    with pytest.raises(ValueError,match="ERR-KICAD-0233"): GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertPolicy(warning_per_role=3,critical_per_role=2)
    with pytest.raises(ValueError,match="ERR-KICAD-0234"): GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptAlertService(sqlite3.connect(":memory:")).evaluate(evaluated_at=datetime(2026,8,6))
