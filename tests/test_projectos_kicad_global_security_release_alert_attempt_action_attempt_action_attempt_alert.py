from datetime import datetime,timedelta,timezone
import sqlite3,pytest
from projectos.identifiers import BusinessId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRepository as Audit
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_alert import (
 GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,
 GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertPolicy as Policy,
 GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertService as Service,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction as Action
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record
from projectos.identifiers import CorrelationId
NOW=datetime(2026,8,6,20,tzinfo=timezone.utc)

def setup_rows(count=0,action=Action.ACKNOWLEDGE,actor=True,code="ERR-X"):
 c=sqlite3.connect(":memory:"); repo=Audit(c)
 for i in range(count): repo.append(Record(BusinessId(f"TRY-{i:08d}"),BusinessId("ALT-00000001"),action,NOW-timedelta(minutes=i),BusinessId("USR-00000001") if actor else None,BusinessId("ROL-00000001"),BusinessId("PERM-00000001"),code,"Abgelehnt",CorrelationId(f"COR-{i:08d}")))
 return c

def test_clear_without_attempts():
 c=setup_rows(); result=Service(c).evaluate(evaluated_at=NOW)
 assert result.level is Level.CLEAR and not result.alert

def test_warning_and_critical_total_thresholds():
 assert Service(setup_rows(3)).evaluate(evaluated_at=NOW).level is Level.WARNING
 assert Service(setup_rows(5)).evaluate(evaluated_at=NOW).level is Level.CRITICAL

def test_action_and_without_actor_thresholds():
 c=setup_rows(2,Action.RESOLVE,False)
 result=Service(c).evaluate(evaluated_at=NOW,policy=Policy(warning_attempts=99,critical_attempts=100,warning_resolve=2,critical_resolve=4,warning_without_actor=2,critical_without_actor=3))
 assert result.level is Level.WARNING and result.resolve_attempts==2 and result.attempts_without_actor==2

def test_critical_denial_code():
 c=setup_rows(1,code="ERR-SPECIAL")
 result=Service(c).evaluate(evaluated_at=NOW,policy=Policy(warning_attempts=99,critical_attempts=100,warning_per_actor=None,critical_per_actor=None,warning_without_actor=None,critical_without_actor=None,critical_denial_codes=("err-special",)))
 assert result.level is Level.CRITICAL and any(x.code=="ERR-KICAD-0278" for x in result.findings)

def test_window_excludes_old_attempts():
 c=setup_rows(3)
 result=Service(c).evaluate(evaluated_at=NOW+timedelta(days=2),policy=Policy(window=timedelta(hours=1)))
 assert result.total_attempts==0 and result.level is Level.CLEAR

def test_invalid_policy_and_naive_time():
 with pytest.raises(ValueError,match="ERR-KICAD-0267"): Policy(window=timedelta(0))
 with pytest.raises(ValueError,match="ERR-KICAD-0270"): Policy(warning_per_actor=5,critical_per_actor=3)
 with pytest.raises(ValueError,match="ERR-KICAD-0271"): Service(setup_rows()).evaluate(evaluated_at=datetime(2026,8,6,20))
