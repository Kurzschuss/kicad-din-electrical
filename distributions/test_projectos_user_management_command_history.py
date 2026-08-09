from uuid import uuid4

import pytest

from .projectos_user_management_command_history import (
    ProjectOSUserManagementCommandHistory,
    ProjectOSUserManagementCommandRecord,
)


def _record(
    *,
    reversible: bool = True,
    history_action: str = "command",
    related_command_id: str | None = None,
) -> ProjectOSUserManagementCommandRecord:
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
        history_action=history_action,
        related_command_id=related_command_id,
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
    assert history.undo_candidate() is record
    assert history.redo_candidate() is None
    assert history.state() == {
        "count": 1,
        "latest_command_id": record.command_id,
        "latest_operation": "user_weight_changed",
        "latest_reversible": True,
        "can_undo": True,
        "can_redo": False,
        "persisted": False,
        "read_only": True,
    }
    assert record.as_dict()["persisted"] is False
    assert record.as_dict()["read_only"] is True

    with pytest.raises(TypeError):
        record.before_values["weight"] = 999

    with pytest.raises(ValueError, match="command_id already recorded"):
        history.append(record)


def test_undo_and_redo_candidates_are_strictly_linear():
    history = ProjectOSUserManagementCommandHistory()
    original = _record()
    history.append(original)
    undo = _record(history_action="undo", related_command_id=original.command_id)
    history.append(undo)

    assert history.undo_candidate() is None
    assert history.redo_candidate() is undo
    assert history.state()["can_redo"] is True

    redo = _record(history_action="redo", related_command_id=undo.command_id)
    history.append(redo)

    assert history.undo_candidate() is redo
    assert history.redo_candidate() is None


def test_non_reversible_latest_command_blocks_undo_without_skipping():
    history = ProjectOSUserManagementCommandHistory()
    reversible = _record()
    history.append(reversible)
    blocker = _record(reversible=False)
    history.append(blocker)

    assert history.undo_candidate() is None
    assert history.redo_candidate() is None
    assert history.state()["can_undo"] is False


def test_related_command_must_already_exist_in_runtime_history():
    history = ProjectOSUserManagementCommandHistory()
    missing = str(uuid4())
    undo = _record(history_action="undo", related_command_id=missing)

    with pytest.raises(ValueError, match="related_command_id is not present"):
        history.append(undo)


def test_command_history_clear_only_resets_runtime_history():
    history = ProjectOSUserManagementCommandHistory()
    record = _record(reversible=False)
    history.append(record)

    history.clear()

    assert history.all() == ()
    assert history.latest() is None
    assert history.state()["persisted"] is False
    assert history.state()["count"] == 0
    assert history.state()["can_undo"] is False
    assert history.state()["can_redo"] is False
