from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_change_trace import ProjectOSUserManagementChangeTraceEmitter
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_undo_redo import ProjectOSUserManagementUndoRedoService


def _tracked_service():
    manager = DinEditorProjectManager()
    emitter = ProjectOSUserManagementChangeTraceEmitter(manager)
    service = ProjectOSUserManagementChangeService(manager, on_change=emitter)
    return manager, emitter, service


def _weight(manager: DinEditorProjectManager, user_id: str) -> int:
    return next(user.weight for user in manager.user_management.users if user.user_id == user_id)


def test_weight_undo_and_redo_are_new_commands_with_new_audit_evidence():
    manager, emitter, service = _tracked_service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer", weight=100)
    original_context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=str(uuid4()),
    )
    service.change_user_weight(target.user_id, 400, command_context=original_context)
    original_record = emitter.command_history.get(original_context.command_id)
    assert original_record is not None
    assert original_record.history_action == "command"
    assert original_record.reversible is True

    undo_redo = ProjectOSUserManagementUndoRedoService(service)
    audit_before_undo = len(manager.sync_log.entries)
    undo_result = undo_redo.undo_latest(actor_user_id=administrator.user_id)

    assert _weight(manager, target.user_id) == 100
    assert undo_result.action == "undo"
    assert undo_result.target_command_id == original_context.command_id
    assert undo_result.command_id != original_context.command_id
    assert undo_result.correlation_id != original_context.correlation_id
    assert len(manager.sync_log.entries) == audit_before_undo + 1

    undo_record = emitter.command_history.get(undo_result.command_id)
    assert undo_record is not None
    assert undo_record.history_action == "undo"
    assert undo_record.related_command_id == original_context.command_id
    assert dict(undo_record.before_values) == {"weight": 400}
    assert dict(undo_record.after_values) == {"weight": 100}
    assert emitter.traces[-1].message.payload["history_action"] == "undo"
    assert emitter.traces[-1].message.payload["related_command_id"] == original_context.command_id
    assert emitter.command_history.get(original_context.command_id) is original_record
    assert emitter.command_history.state()["can_undo"] is False
    assert emitter.command_history.state()["can_redo"] is True

    audit_before_redo = len(manager.sync_log.entries)
    redo_result = undo_redo.redo_latest(actor_user_id=administrator.user_id)

    assert _weight(manager, target.user_id) == 400
    assert redo_result.action == "redo"
    assert redo_result.target_command_id == undo_result.command_id
    assert redo_result.command_id not in {original_context.command_id, undo_result.command_id}
    assert redo_result.correlation_id not in {original_context.correlation_id, undo_result.correlation_id}
    assert len(manager.sync_log.entries) == audit_before_redo + 1

    redo_record = emitter.command_history.get(redo_result.command_id)
    assert redo_record is not None
    assert redo_record.history_action == "redo"
    assert redo_record.related_command_id == undo_result.command_id
    assert dict(redo_record.before_values) == {"weight": 100}
    assert dict(redo_record.after_values) == {"weight": 400}
    assert emitter.traces[-1].message.payload["history_action"] == "redo"
    assert emitter.command_history.state()["can_undo"] is True
    assert emitter.command_history.state()["can_redo"] is False


def test_non_reversible_latest_command_blocks_undo_without_skipping_history():
    manager, emitter, service = _tracked_service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer")
    service.change_user_weight(
        target.user_id,
        300,
        command_context=ProjectOSUserManagementCommandContext(
            actor_user_id=administrator.user_id,
            correlation_id=str(uuid4()),
        ),
    )
    service.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        command_context=ProjectOSUserManagementCommandContext(
            actor_user_id=administrator.user_id,
            correlation_id=str(uuid4()),
        ),
    )
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())

    undo_redo = ProjectOSUserManagementUndoRedoService(service)
    with pytest.raises(ValueError, match="no reversible command available for undo"):
        undo_redo.undo_latest(actor_user_id=administrator.user_id)

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count


def test_state_drift_blocks_undo_fail_closed():
    manager, emitter, service = _tracked_service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer", weight=100)
    service.change_user_weight(
        target.user_id,
        300,
        command_context=ProjectOSUserManagementCommandContext(
            actor_user_id=administrator.user_id,
            correlation_id=str(uuid4()),
        ),
    )

    untracked = ProjectOSUserManagementChangeService(manager)
    untracked.change_user_weight(target.user_id, 999)
    before = manager.user_management.as_dict()
    history_count = len(emitter.command_history.all())

    undo_redo = ProjectOSUserManagementUndoRedoService(service)
    with pytest.raises(ValueError, match="current user weight does not match undo candidate"):
        undo_redo.undo_latest(actor_user_id=administrator.user_id)

    assert manager.user_management.as_dict() == before
    assert len(emitter.command_history.all()) == history_count


def test_new_normal_command_after_undo_closes_redo_branch():
    manager, emitter, service = _tracked_service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer", weight=100)
    service.change_user_weight(
        target.user_id,
        300,
        command_context=ProjectOSUserManagementCommandContext(
            actor_user_id=administrator.user_id,
            correlation_id=str(uuid4()),
        ),
    )
    undo_redo = ProjectOSUserManagementUndoRedoService(service)
    undo_redo.undo_latest(actor_user_id=administrator.user_id)
    assert emitter.command_history.state()["can_redo"] is True

    service.change_user_weight(
        target.user_id,
        150,
        command_context=ProjectOSUserManagementCommandContext(
            actor_user_id=administrator.user_id,
            correlation_id=str(uuid4()),
        ),
    )

    assert emitter.command_history.state()["can_redo"] is False
    with pytest.raises(ValueError, match="no command available for redo"):
        undo_redo.redo_latest(actor_user_id=administrator.user_id)


def test_undo_requires_new_correlation_and_existing_actor_before_mutation():
    manager, emitter, service = _tracked_service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer", weight=100)
    original_context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=str(uuid4()),
    )
    service.change_user_weight(target.user_id, 300, command_context=original_context)
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())
    undo_redo = ProjectOSUserManagementUndoRedoService(service)

    with pytest.raises(ValueError, match="requires a new correlation_id"):
        undo_redo.undo_latest(
            actor_user_id=administrator.user_id,
            correlation_id=original_context.correlation_id,
        )

    with pytest.raises(ValueError, match="actor user does not exist"):
        undo_redo.undo_latest(actor_user_id=str(uuid4()))

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count
