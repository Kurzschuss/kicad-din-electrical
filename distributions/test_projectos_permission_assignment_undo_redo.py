from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_user_management_lineage import ZCockpitUserManagementLineageView


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def _grant_control_permissions(bootstrap, actor_id: str, *, undo: bool = True, redo: bool = True):
    permissions = [
        "project.user_management.permission.assign",
        "project.user_management.permission.revoke",
        "project.user_management.permission.regrant",
    ]
    if undo:
        permissions.append("project.user_management.permission.undo_assign")
    if redo:
        permissions.append("project.user_management.permission.redo_assign")
    for permission in permissions:
        bootstrap.command_assign_permission(
            user_id=actor_id,
            permission=permission,
            source_type="direct",
            effect="allow",
        )


def test_permission_assignment_undo_redo_uses_revocation_and_new_regrant_ids():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    target = bootstrap.create_user("Ziel")
    _grant_control_permissions(bootstrap, actor.user_id)
    runtime = build_projectos_user_management_runtime(manager)

    original_context = _context(actor.user_id)
    original = runtime.changes.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        command_context=original_context,
    )
    assert runtime.emitter.command_history.latest().operation == "permission_assigned"
    assert runtime.emitter.command_history.latest().reversible is True

    undo1 = runtime.undo_redo.undo_latest(actor_user_id=actor.user_id)
    first_revocation = manager.user_management.permission_revocations[-1]
    assert undo1.operation == "permission_revoked"
    assert undo1.assignment_id == original.assignment_id
    assert undo1.revocation_id == first_revocation.revocation_id
    assert original in manager.user_management.permission_assignments
    undo_record = runtime.emitter.command_history.latest()
    assert undo_record.history_action == "undo"
    assert undo_record.operation == "permission_revoked"
    assert undo_record.reversible is True
    assert runtime.changes.last_authorization["policy_key"] == "undo:permission_revoked"

    redo1 = runtime.undo_redo.redo_latest(actor_user_id=actor.user_id)
    first_successor = manager.user_management.permission_assignments[-1]
    assert redo1.operation == "permission_regranted"
    assert first_successor.assignment_id != original.assignment_id
    assert first_successor.metadata["predecessor_assignment_id"] == original.assignment_id
    assert runtime.changes.last_authorization["policy_key"] == "redo:permission_regranted"
    redo_record = runtime.emitter.command_history.latest()
    assert redo_record.history_action == "redo"
    assert redo_record.operation == "permission_regranted"
    assert redo_record.reversible is True

    undo2 = runtime.undo_redo.undo_latest(actor_user_id=actor.user_id)
    assert undo2.assignment_id == first_successor.assignment_id
    redo2 = runtime.undo_redo.redo_latest(actor_user_id=actor.user_id)
    second_successor = manager.user_management.permission_assignments[-1]
    assert second_successor.assignment_id not in {original.assignment_id, first_successor.assignment_id}
    assert second_successor.metadata["predecessor_assignment_id"] == first_successor.assignment_id
    assert redo2.assignment_id == second_successor.assignment_id

    actions = [entry["action"] for entry in manager.sync_log.entries]
    assert actions[-5:] == [
        "permission_assigned",
        "permission_revoked",
        "permission_regranted",
        "permission_revoked",
        "permission_regranted",
    ]
    lineage = ZCockpitUserManagementLineageView(manager).state()
    assert lineage["permission_regrant_count"] == 2
    assert lineage["attention_required"] is False


def test_normal_permission_revocation_remains_non_reversible():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    target = bootstrap.create_user("Ziel")
    _grant_control_permissions(bootstrap, actor.user_id)
    runtime = build_projectos_user_management_runtime(manager)

    assignment = runtime.changes.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        command_context=_context(actor.user_id),
    )
    runtime.changes.command_revoke_permission(
        assignment_id=assignment.assignment_id,
        revoked_at="2026-08-09T13:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Manueller Widerruf",
        command_context=_context(actor.user_id),
    )

    latest = runtime.emitter.command_history.latest()
    assert latest.operation == "permission_revoked"
    assert latest.history_action == "command"
    assert latest.reversible is False
    assert runtime.emitter.command_history.undo_candidate() is None
    with pytest.raises(ValueError, match="no reversible command"):
        runtime.undo_redo.undo_latest(actor_user_id=actor.user_id)


def test_missing_permission_undo_right_denies_without_side_effects():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    target = bootstrap.create_user("Ziel")
    _grant_control_permissions(bootstrap, actor.user_id, undo=False)
    runtime = build_projectos_user_management_runtime(manager)

    runtime.changes.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        command_context=_context(actor.user_id),
    )
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    trace_count = len(runtime.emitter.traces)
    history_count = len(runtime.emitter.command_history.all())

    with pytest.raises(PermissionError, match=r"undo:permission_revoked \(not_granted\)"):
        runtime.undo_redo.undo_latest(actor_user_id=actor.user_id)

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(runtime.emitter.traces) == trace_count
    assert len(runtime.emitter.command_history.all()) == history_count
