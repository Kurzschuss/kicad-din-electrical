from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_policy import ProjectOSUserManagementCommandPolicy
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_user_management_command_diagnostics import ZCockpitUserManagementCommandDiagnosticsView
from .z_cockpit_user_management_persistence import ZCockpitUserManagementPersistenceView


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(actor_user_id=actor_user_id, correlation_id=str(uuid4()))


def test_bundle_roundtrip_preserves_role_assignment_and_termination(tmp_path):
    manager = DinEditorProjectManager()
    actor = ProjectOSUserProfile("Projektleitung")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=manager.project_id, user_id=user.user_id, role_type="deputy")
    termination = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=manager.project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T10:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Stellvertretung beendet",
        source_reference="ROLE-99",
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(actor, user),
        project_roles=(role,),
        role_assignment_terminations=(termination,),
    ))
    path = manager.save(tmp_path / "role-termination.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)

    assert loaded.user_management.project_roles[0].role_assignment_id == role.role_assignment_id
    assert loaded.user_management.role_assignment_terminations[0].termination_id == termination.termination_id
    assert loaded.user_management.role_assignment_terminations[0].role_assignment_id == role.role_assignment_id
    persistence = ZCockpitUserManagementPersistenceView(loaded).state()
    assert persistence["persisted_counts"]["role_assignment_terminations"] == 1


def test_terminated_high_risk_role_no_longer_grants_command_permission():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    security = bootstrap.create_user("Security")
    deputy = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Freigabe")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=security.user_id,
        permission="project.user_management.role.terminate",
        source_type="direct",
        effect="allow",
    )
    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=security.user_id,
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="absence",
        triggered_by_user_id=security.user_id,
    )
    request = bootstrap.command_request_approval(
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=security.user_id,
        risk_class="high",
        requested_at="2026-08-09T09:00:00+00:00",
    )
    bootstrap.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T09:01:00+00:00",
    )
    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_permission_map={"deputy": ["project.user_management.weight.change"]},
        role_risk_class_map={"deputy": "high"},
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)

    before = runtime.authorization.evaluate("user_weight_changed", _context(deputy.user_id))
    assert before["allowed"] is True
    assert before["role_derived_assignment_count"] == 1
    assert before["terminated_granting_role_count"] == 0

    runtime.changes.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T00:00:00+00:00",
        ended_by_user_id=security.user_id,
        reason="Administrative Rollenzuweisung beendet",
        command_context=_context(security.user_id),
    )
    trace_count = len(runtime.emitter.traces)
    audit_count = len(manager.sync_log.entries)
    history_count = len(runtime.emitter.command_history.all())

    after = runtime.authorization.evaluate("user_weight_changed", _context(deputy.user_id))
    assert after["allowed"] is False
    assert after["decision"] == "not_granted"
    assert after["role_derived_assignment_count"] == 0
    assert after["terminated_granting_role_count"] == 1

    with pytest.raises(PermissionError, match="not_granted"):
        runtime.changes.change_user_weight(
            target.user_id,
            500,
            command_context=_context(deputy.user_id),
        )
    assert next(item.weight for item in manager.user_management.users if item.user_id == target.user_id) == 100
    assert len(runtime.emitter.traces) == trace_count
    assert len(manager.sync_log.entries) == audit_count
    assert len(runtime.emitter.command_history.all()) == history_count

    diagnostics = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()
    assert diagnostics["last_decision"] == "not_granted"
    assert diagnostics["terminated_granting_role_count"] == 1
    assert diagnostics["role_termination_blocked"] is True
    assert diagnostics["revocation_blocked"] is False
