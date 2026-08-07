from datetime import datetime, timezone
import sqlite3
import pytest
from projectos.identifiers import BusinessId, CorrelationId
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_authorization import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE as ACK,
)
from projectos.kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_action_attempt_audit import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRepository as Repository,
)
NOW=datetime(2026,8,6,22,tzinfo=timezone.utc)

def _record(**changes):
    values=dict(attempt_id=BusinessId("ATT-01120001"),alert_id=BusinessId("ALT-01100001"),action=Action.ACKNOWLEDGE,attempted_at=NOW,actor_id=None,acting_role=BusinessId("ROL-00000001"),permission_id=ACK,denial_code="ERR-KICAD-0329",denial_reason="Berechtigung fehlt",correlation_id=CorrelationId("COR-01120001")); values.update(changes); return Record(**values)

def test_roundtrip_preserves_missing_actor():
    repo=Repository(sqlite3.connect(":memory:")); record=_record(); repo.append(record)
    assert repo.list_for_alert(record.alert_id)==(record,)

def test_requires_timezone_code_and_reason():
    repo=Repository(sqlite3.connect(":memory:"))
    with pytest.raises(ValueError,match="ERR-KICAD-0331"): repo.append(_record(attempted_at=datetime(2026,8,6,22)))
    with pytest.raises(ValueError,match="ERR-KICAD-0332"): repo.append(_record(denial_code=" "))
    with pytest.raises(ValueError,match="ERR-KICAD-0333"): repo.append(_record(denial_reason=" "))

def test_attempt_id_is_unique():
    repo=Repository(sqlite3.connect(":memory:")); record=_record(); repo.append(record)
    with pytest.raises(ValueError,match="ERR-KICAD-0334"): repo.append(record)
