from uuid import uuid4

import pytest

from .projectos_user_management_command_history import (
    ProjectOSUserManagementCommandHistory,
    ProjectOSUserManagementCommandRecord,
)


def _record(*, reversible: bool = True) -> ProjectOSUserManagementCommandRecord:
    return ProjectOSUserManagementCommandRecord(
        command_id=str(uuid4()),
        project_id=str(uuid4()),
        operation="user_weight_changed",
        actor_user_id=str(uuid4()),
        correlation_id=str(uuid4()),
        causation_id=None,
        reference=str(uuid4()),
        recorded_at="2026-08-09T10:00:00+00:00",
        reversible=reversible,
        before_values={"weight": 100},
        after_values={"weight": 250},
        message_id=str(uuid4()),
        audit_reference="user:test",
    )


def test_command_history_is_append_only_read_only_runtime_metadata():
    history = ProjectOSUserManagementCommandHistory()
    record = _record()

    history.append(record)

    assert history.all() == (record,)
    assert history.get(record.command_id) is record
    assert history.latest() is record
    assert history.state() == {
        "count": 1,
        "latest_command_id": record.command_id,
        "latest_operation": "user_weight_changed",
        "latest_reversible": True,
        "persisted": False,
        "read_only": True,
    }
    assert record.as_dict()["persisted"] is False
    assert record.as_dict()["read_only"] is True

    with pytest.raises(TypeError):
        record.before_values["weight"] = 999

    with pytest.raises(ValueError, match="command_id already recorded"):
        history.append(record)


def test_command_history_clear_only_resets_runtime_history():
    history = ProjectOSUserManagementCommandHistory()
    record = _record(reversible=False)
    history.append(record)

    history.clear()

    assert history.all() == ()
    assert history.latest() is None
    assert history.state()["persisted"] is False
    assert history.state()["count"] == 0
