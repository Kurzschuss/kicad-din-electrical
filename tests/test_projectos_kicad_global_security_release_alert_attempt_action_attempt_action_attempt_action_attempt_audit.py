from datetime import datetime, timezone
import sqlite3, pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action, PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE as PERM
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRepository as Repository
NOW=datetime(2026,8,6,21,tzinfo=timezone.utc)

def test_roundtrip_with_missing_actor():
    repo=Repository(sqlite3.connect(":memory:")); aid=BusinessId("ALT-01070001")
    record=Record(BusinessId("TRY-01070001"),aid,Action.ACKNOWLEDGE,NOW,None,BusinessId("ROL-00000001"),PERM,"ERR-KICAD-0292","Nicht berechtigt",CorrelationId("COR-01070001"))
    repo.append(record)
    assert repo.list_for_alert(aid)==(record,)

def test_duplicate_attempt_id_is_rejected():
    repo=Repository(sqlite3.connect(":memory:")); record=Record(BusinessId("TRY-01070002"),BusinessId("ALT-01070002"),Action.ACKNOWLEDGE,NOW,BusinessId("USR-1"),BusinessId("ROL-1"),PERM,"ERR-KICAD-0293","Falsche Rolle",CorrelationId("COR-01070002"))
    repo.append(record)
    with pytest.raises(ValueError,match="ERR-KICAD-0297"): repo.append(record)

def test_code_reason_and_timezone_are_required():
    repo=Repository(sqlite3.connect(":memory:")); base=dict(attempt_id=BusinessId("TRY-01070003"),alert_id=BusinessId("ALT-01070003"),action=Action.ACKNOWLEDGE,attempted_at=NOW,actor_id=None,acting_role=BusinessId("ROL-1"),permission_id=PERM,denial_code="ERR",denial_reason="Grund",correlation_id=CorrelationId("COR-01070003"))
    with pytest.raises(ValueError,match="ERR-KICAD-0295"): repo.append(Record(**{**base,"denial_code":" "}))
    with pytest.raises(ValueError,match="ERR-KICAD-0296"): repo.append(Record(**{**base,"denial_reason":" "}))
    with pytest.raises(ValueError,match="ERR-KICAD-0294"): repo.append(Record(**{**base,"attempted_at":datetime(2026,8,6,21)}))
