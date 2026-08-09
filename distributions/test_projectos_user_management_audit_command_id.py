from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_runtime import build_projectos_user_management_runtime


def test_user_management_audit_command_id_survives_bundle_roundtrip(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission="project.user_management.weight.change",
        source_type="direct",
        effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=str(uuid4()),
    )

    runtime.changes.change_user_weight(target.user_id, 275, command_context=context)
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.traces[-1].audit_entry["command_id"] == context.command_id

    path = manager.save(tmp_path / "audit-command-id.json")
    loaded = DinEditorProjectManager()
    loaded.load(path)

    assert loaded.sync_log.entries[-1]["command_id"] == context.command_id
    assert loaded.sync_log.entries[-1]["correlation_id"] == context.correlation_id
