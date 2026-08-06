from datetime import datetime, timedelta, timezone
import sqlite3, pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRepository as Repository
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_search import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter as Filter, GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchService as Search
NOW=datetime(2026,8,6,21,tzinfo=timezone.utc)

def _record(i,*,action=Action.ACKNOWLEDGE,actor=True,reason="Berechtigung fehlt"):
    return Record(BusinessId(f"TRY-0108{i:04d}"),BusinessId(f"ALT-0105{i%2:04d}"),action,NOW+timedelta(minutes=i),BusinessId(f"USR-0108{i:04d}") if actor else None,BusinessId("ROL-01080001"),BusinessId("PER-01080001"),"ERR-KICAD-0292",reason,CorrelationId(f"COR-0108{i:04d}"))

def _service():
    connection=sqlite3.connect(":memory:"); repo=Repository(connection)
    for record in (_record(1),_record(2,action=Action.RESOLVE,actor=False,reason="Rolle unpassend"),_record(3)):
        repo.append(record)
    return Search(connection)

def test_combined_filter_and_free_text():
    service=_service(); page=service.search(Filter(action=Action.RESOLVE,free_text="unpassend"))
    assert page.total_items==1 and page.items[0].actor_id is None

def test_pagination_is_stable_and_newest_first():
    service=_service(); first=service.search(page=1,page_size=2); second=service.search(page=2,page_size=2)
    assert [str(x.attempt_id) for x in first.items]==["TRY-01080003","TRY-01080002"]
    assert len(second.items)==1 and first.has_next and second.has_previous

def test_diagnostic_counts_actions_and_missing_actor():
    diagnostic=_service().diagnose()
    assert diagnostic.total_attempts==3 and diagnostic.affected_alerts==2
    assert diagnostic.acknowledge_attempts==2 and diagnostic.resolve_attempts==1
    assert diagnostic.attempts_without_actor==1 and diagnostic.top_denial_codes[0][1]==3

def test_empty_diagnostic():
    connection=sqlite3.connect(":memory:"); Repository(connection)
    diagnostic=Search(connection).diagnose()
    assert diagnostic.total_attempts==0 and diagnostic.first_attempt_at is None and diagnostic.last_attempt_at is None

def test_invalid_parameters_are_rejected():
    service=_service()
    with pytest.raises(ValueError,match="ERR-KICAD-0302"): service.search(page=0)
    with pytest.raises(ValueError,match="ERR-KICAD-0303"): service.search(page_size=201)
    with pytest.raises(ValueError,match="ERR-KICAD-0300"): Filter(from_at=datetime(2026,8,6,21))
    with pytest.raises(ValueError,match="ERR-KICAD-0301"): Filter(from_at=NOW,to_at=NOW-timedelta(minutes=1))
