from pathlib import Path
from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_change_trace import ProjectOSUserManagementChangeTraceEmitter
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext


def _tracked():
    manager = DinEditorProjectManager()
    emitter = ProjectOSUserManagementChangeTraceEmitter(manager)
    service = ProjectOSUserManagementChangeService(manager, on_change=emitter)
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer", weight=100)
    return manager, emitter, service, administrator.user_id, target.user_id


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def _weight(manager: DinEditorProjectManager, user_id: str) -> int:
    return next(user.weight for user in manager.user_management.users if user.user_id == user_id)


def test_successful_load_resets_runtime_history_and_realigns_existing_service(tmp_path: Path):
    manager, emitter, service, administrator_id, target_id = _tracked()
    path = manager.save(tmp_path / "projectos-load.json")
    service.change_user_weight(target_id, 300, command_context=_context(administrator_id))
    assert len(emitter.command_history.all()) == 3

    manager.load(path, discard_changes=True)

    assert _weight(manager, target_id) == 100
    assert emitter.command_history.all() == ()

    service.change_user_weight(target_id, 225, command_context=_context(administrator_id))

    assert _weight(manager, target_id) == 225
    assert len(emitter.command_history.all()) == 1
    assert len(emitter.traces) == 1
    assert emitter.audit_log is manager.sync_log
    assert emitter.command_history.latest().project_id == manager.project_id


def test_discard_changes_resets_runtime_history_without_touching_saved_domain_state(tmp_path: Path):
    manager, emitter, service, administrator_id, target_id = _tracked()
    manager.save(tmp_path / "projectos-discard.json")
    service.change_user_weight(target_id, 450, command_context=_context(administrator_id))
    assert emitter.command_history.state()["can_undo"] is True

    manager.discard_changes()

    assert _weight(manager, target_id) == 100
    assert emitter.command_history.all() == ()
    assert emitter.command_history.state()["can_undo"] is False
    assert emitter.command_history.state()["can_redo"] is False


def test_new_project_resets_runtime_history_and_old_project_references_are_not_reused():
    manager, emitter, service, administrator_id, target_id = _tracked()
    old_project_id = manager.project_id
    assert len(emitter.command_history.all()) == 2

    manager.new_project(discard_changes=True)

    assert manager.project_id != old_project_id
    assert manager.user_management.users == ()
    assert emitter.command_history.all() == ()

    new_administrator = service.create_user("Neuer Administrator")
    new_target = service.create_user("Neuer Zielbenutzer", weight=150)
    service.change_user_weight(
        new_target.user_id,
        275,
        command_context=_context(new_administrator.user_id),
    )

    assert _weight(manager, new_target.user_id) == 275
    assert len(emitter.command_history.all()) == 3
    assert {record.project_id for record in emitter.command_history.all()} == {manager.project_id}
    assert all(record.reference != target_id for record in emitter.command_history.all())


def test_recover_resets_runtime_history_and_uses_recovered_audit_log(tmp_path: Path):
    manager, emitter, service, administrator_id, target_id = _tracked()
    path = manager.save(tmp_path / "projectos-recover.json")

    service.change_user_weight(target_id, 300, command_context=_context(administrator_id))
    manager.save(path)
    assert manager.recovery_status()["can_recover"] is True
    assert len(emitter.command_history.all()) == 3

    manager.recover(path)

    assert _weight(manager, target_id) == 100
    assert emitter.command_history.all() == ()

    service.change_user_weight(target_id, 200, command_context=_context(administrator_id))

    assert _weight(manager, target_id) == 200
    assert len(emitter.command_history.all()) == 1
    assert emitter.audit_log is manager.sync_log
    assert emitter.command_history.latest().project_id == manager.project_id
