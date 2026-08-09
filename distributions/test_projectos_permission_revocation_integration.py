import json
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_permission_revocation import ProjectOSPermissionRevocation
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_user_management_command_diagnostics import ZCockpitUserManagementCommandDiagnosticsView


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def test_bundle_v4_roundtrip_preserves_assignment_and_revocation(tmp_path):
    manager = DinEditorProjectManager()
    user = ProjectOSUserProfile("Engineering")
    actor = ProjectOSUserProfile("Administration")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    revocation = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=manager.project_id,
        user_id=user.user_id,
        scope=assignment.scope,
        revoked_at="2026-08-09T10:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Projektzugriff beendet",
        source_reference="CHANGE-42",
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(user, actor),
        permission_assignments=(assignment,),
        permission_revocations=(revocation,),
    ))
    path = manager.save(tmp_path / "revocation.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)

    assert loaded.user_management.permission_assignments[0].assignment_id == assignment.assignment_id
    assert loaded.user_management.permission_revocations[0].revocation_id == revocation.revocation_id
    assert loaded.user_management.permission_revocations[0].assignment_id == assignment.assignment_id
    assert loaded.user_management.as_dict()["version"] == 2


def test_bundle_v4_with_user_management_v1_loads_and_explicit_save_upgrades_to_v2(tmp_path):
    manager = DinEditorProjectManager()
    user = ProjectOSUserProfile("Altbestand")
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(user,),
    ))
    path = manager.save(tmp_path / "legacy-user-management.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["user_management"]["version"] = 1
    payload["user_management"].pop("permission_revocations")
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = DinEditorProjectManager()
    loaded.load(path)

    assert loaded.user_management.permission_revocations == ()
    assert json.loads(path.read_text(encoding="utf-8"))["user_management"]["version"] == 1

    loaded.save()
    upgraded = json.loads(path.read_text(encoding="utf-8"))
    assert upgraded["version"] == 4
    assert upgraded["user_management"]["version"] == 2
    assert upgraded["user_management"]["permission_revocations"] == []


def test_revoked_command_permission_blocks_later_command_without_side_effects():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    security = bootstrap.create_user("Security")
    operator = bootstrap.create_user("Operator")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=security.user_id,
        permission="project.user_management.permission.revoke",
        source_type="direct",
        effect="allow",
    )
    operator_weight_right = bootstrap.command_assign_permission(
        user_id=operator.user_id,
        permission="project.user_management.weight.change",
        source_type="direct",
        effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)

    runtime.changes.command_revoke_permission(
        assignment_id=operator_weight_right.assignment_id,
        revoked_at="2026-08-09T00:00:00+00:00",
        revoked_by_user_id=security.user_id,
        reason="Administrative Berechtigung entzogen",
        command_context=_context(security.user_id),
    )
    trace_count = len(runtime.emitter.traces)
    audit_count = len(manager.sync_log.entries)
    history_count = len(runtime.emitter.command_history.all())

    with pytest.raises(PermissionError, match="not_granted"):
        runtime.changes.change_user_weight(
            target.user_id,
            500,
            command_context=_context(operator.user_id),
        )

    assert next(item.weight for item in manager.user_management.users if item.user_id == target.user_id) == 100
    assert len(runtime.emitter.traces) == trace_count
    assert len(manager.sync_log.entries) == audit_count
    assert len(runtime.emitter.command_history.all()) == history_count

    diagnostics = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()
    assert diagnostics["last_decision"] == "not_granted"
    assert diagnostics["revoked_assignment_count"] == 1
    assert diagnostics["revocation_blocked"] is True
    assert diagnostics["attention_required"] is True
