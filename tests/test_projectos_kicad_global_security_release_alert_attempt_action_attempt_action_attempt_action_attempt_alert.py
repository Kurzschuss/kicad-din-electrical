from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRepository as Repo
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_alert import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level, GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertPolicy as Policy, GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertService as Service
NOW=datetime(2026,8,6,21,tzinfo=timezone.utc)

def _record(n,*,action=Action.ACKNOWLEDGE,actor="USR-00000001",role="ROL-00000001",code="DENIED",minutes=0):
    return Record(BusinessId(f"ATM-0109{n:04d}"),BusinessId("ALT-01050001"),action,NOW-timedelta(minutes=minutes),BusinessId(actor) if actor else None,BusinessId(role),BusinessId("PERM-00000001"),code,"Abgelehnt",CorrelationId(f"COR-0109{n:04d}"))

def test_clear_without_attempts():
    db=sqlite3.connect(":memory:"); Repo(db)
    assert Service(db).evaluate(evaluated_at=NOW).level is Level.CLEAR

def test_warning_and_critical_actor_threshold():
    db=sqlite3.connect(":memory:"); repo=Repo(db)
    for n in range(3): repo.append(_record(n))
    assert Service(db).evaluate(evaluated_at=NOW).level is Level.WARNING
    repo.append(_record(3)); repo.append(_record(4))
    result=Service(db).evaluate(evaluated_at=NOW)
    assert result.level is Level.CRITICAL
    assert any(x.code=="ERR-KICAD-0310" for x in result.findings)

def test_action_threshold_and_critical_code():
    db=sqlite3.connect(":memory:"); repo=Repo(db)
    repo.append(_record(1,action=Action.RESOLVE,code="ROLE-MISMATCH"))
    policy=Policy(warning_attempts=9,critical_attempts=10,warning_resolve=1,critical_resolve=2,critical_denial_codes=("role-mismatch",))
    result=Service(db).evaluate(evaluated_at=NOW,policy=policy)
    assert result.level is Level.CRITICAL
    assert result.resolve_attempts==1
    assert any(x.code=="ERR-KICAD-0315" for x in result.findings)

def test_window_excludes_old_attempts():
    db=sqlite3.connect(":memory:"); repo=Repo(db)
    repo.append(_record(1,minutes=180))
    result=Service(db).evaluate(evaluated_at=NOW,policy=Policy(window=timedelta(hours=1)))
    assert result.total_attempts==0

def test_without_actor_threshold():
    db=sqlite3.connect(":memory:"); repo=Repo(db)
    repo.append(_record(1,actor=""))
    result=Service(db).evaluate(evaluated_at=NOW)
    assert result.level is Level.WARNING
    assert result.attempts_without_actor==1

def test_invalid_policy_and_naive_time():
    with pytest.raises(ValueError,match="ERR-KICAD-0304"): Policy(window=timedelta(0))
    with pytest.raises(ValueError,match="ERR-KICAD-0307"): Policy(warning_per_role=3,critical_per_role=2)
    db=sqlite3.connect(":memory:"); Repo(db)
    with pytest.raises(ValueError,match="ERR-KICAD-0308"): Service(db).evaluate(evaluated_at=datetime(2026,8,6,21))
