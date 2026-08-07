from datetime import datetime, timedelta, timezone
import sqlite3, pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security import GlobalSecurityResponsibilityType
from projectos.kicad_global_security_release_alert_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction as Action
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRepository as Repository,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_search import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter as Filter,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchService as Service,
)
NOW=datetime(2026,8,6,18,tzinfo=timezone.utc)

def _record(i,action=Action.ACKNOWLEDGE,actor=True,code="ERR-KICAD-0255"):
    return Record(BusinessId(f"TRY-0103-{i:04d}"),BusinessId(f"ALT-0103-{i%2:04d}"),action,NOW+timedelta(minutes=i),BusinessId(f"USR-0103-{i%2:04d}") if actor else None,BusinessId(f"ROL-0103-{i%2:04d}"),BusinessId(f"PERM-0103-{i%2:04d}"),code,f"Ablehnung {i}",CorrelationId(f"COR-0103{i:04d}"))

def _setup():
    connection=sqlite3.connect(":memory:"); repo=Repository(connection)
    repo.append(_record(1)); repo.append(_record(2,Action.RESOLVE,False,"ERR-KICAD-0256")); repo.append(_record(3))
    return Service(connection)

def test_combined_filter_and_text_search():
    service=_setup(); page=service.search(Filter(action=Action.RESOLVE,reason_text="Ablehnung 2"))
    assert page.total_items==1 and page.items[0].actor_id is None

def test_stable_pagination_newest_first():
    service=_setup(); first=service.search(page=1,page_size=2); second=service.search(page=2,page_size=2)
    assert [str(x.attempt_id) for x in first.items]==["TRY-0103-0003","TRY-0103-0002"]
    assert first.has_next and second.has_previous and second.total_pages==2

def test_diagnostic_aggregates_actions_and_missing_actor():
    diagnostic=_setup().diagnostic()
    assert diagnostic.total_attempts==3 and diagnostic.acknowledge_attempts==2 and diagnostic.resolve_attempts==1
    assert diagnostic.attempts_without_actor==1 and diagnostic.distinct_alerts==2

def test_empty_diagnostic():
    connection=sqlite3.connect(":memory:"); Repository(connection)
    diagnostic=Service(connection).diagnostic()
    assert diagnostic.total_attempts==0 and diagnostic.first_attempt_at is None and diagnostic.latest_attempt_at is None

def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError,match="ERR-KICAD-0263"): Filter(from_timestamp=datetime(2026,8,6,18))
    with pytest.raises(ValueError,match="ERR-KICAD-0264"): Filter(from_timestamp=NOW,until_timestamp=NOW-timedelta(seconds=1))
    service=_setup()
    with pytest.raises(ValueError,match="ERR-KICAD-0265"): service.search(page=0)
    with pytest.raises(ValueError,match="ERR-KICAD-0266"): service.search(page_size=201)
