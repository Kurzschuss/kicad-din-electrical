from datetime import datetime, timezone
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .projectos_user_project_roles import ProjectOSUserProjectRole, ProjectOSUserProjectRoleRegistry


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(actor_user_id=actor_user_id, correlation_id=str(uuid4()))


def test_role_assignment_termination_is_effective_from_ended_at_and_keeps_role_history():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Stellvertretung")
    actor = ProjectOSUserProfile("Projektleitung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    termination = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T12:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Stellvertretung dauerhaft beendet",
        source_reference="ROLE-42",
    )
    registry = ProjectOSUserProjectRoleRegistry([role], [termination])

    before = registry.state(project_id=project_id, user=user, at=datetime(2026, 8, 9, 11, 59, tzinfo=timezone.utc))
    after = registry.state(project_id=project_id, user=user, at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc))

    assert len(before["active_roles"]) == 1
    assert before["termination_count"] == 0
    assert after["active_roles"] == []
    assert after["termination_count"] == 1
    assert after["terminated_roles"][0]["role"]["role_assignment_id"] == role.role_assignment_id
    assert after["terminated_roles"][0]["termination"]["termination_id"] == termination.termination_id


def test_approved_high_risk_activation_loses_permission_after_assignment_termination():
    project_id = str(uuid4())
    principal = ProjectOSUserProfile("Projektleitung")
    user = ProjectOSUserProfile("Stellvertretung")
    approver = ProjectOSUserProfile("Freigabe")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
    )
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T10:00:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T10:01:00+00:00",
    )
    termination = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T12:00:00+00:00",
        ended_by_user_id=principal.user_id,
        reason="Stellvertretungsauftrag beendet",
    )
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role],
        activations=[activation],
        role_terminations=[termination],
        approval_requests=[request],
        approvals=[approval],
        risk_class_map={"deputy": "high"},
    )

    before = evaluator.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=datetime(2026, 8, 9, 11, 59, tzinfo=timezone.utc),
    )
    after = evaluator.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc),
    )
    after_state = evaluator.state(
        project_id=project_id,
        user=user,
        at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc),
    )

    assert len(before) == 1
    assert after == ()
    assert len(after_state["terminated_assigned_roles"]) == 1


def test_user_management_rejects_duplicate_or_mismatched_role_assignment_termination():
    project_id = str(uuid4())
    actor = ProjectOSUserProfile("Projektleitung")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    first = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T12:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Beendet",
    )
    second = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T13:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Doppelt beendet",
    )
    with pytest.raises(ValueError, match="already terminated"):
        ProjectOSUserManagementState(
            project_id=project_id,
            users=(actor, user),
            project_roles=(role,),
            role_assignment_terminations=(first, second),
        )

    wrong_scope = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope="project:other",
        ended_at="2026-08-09T12:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Falscher Scope",
    )
    with pytest.raises(ValueError, match="scope does not match"):
        ProjectOSUserManagementState(
            project_id=project_id,
            users=(actor, user),
            project_roles=(role,),
            role_assignment_terminations=(wrong_scope,),
        )


def test_secured_termination_command_keeps_role_and_blocks_new_activation():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Projektleitung")
    user = bootstrap.create_user("Stellvertretung")
    bootstrap.command_assign_permission(
        user_id=actor.user_id,
        permission="project.user_management.role.terminate",
        source_type="direct",
        effect="allow",
    )
    role = bootstrap.command_assign_project_role(
        user_id=user.user_id,
        role_type="deputy",
        assigned_by_user_id=actor.user_id,
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(actor.user_id)

    termination = runtime.changes.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T00:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Stellvertretung beendet",
        source_reference="ROLE-END-17",
        command_context=context,
    )

    assert len(manager.user_management.project_roles) == 1
    assert manager.user_management.project_roles[0].role_assignment_id == role.role_assignment_id
    assert manager.user_management.role_assignment_terminations == (termination,)
    assert runtime.emitter.traces[-1].operation == "project_role_assignment_terminated"
    assert runtime.emitter.traces[-1].reference == termination.termination_id
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.command_history.latest().reversible is False

    trace_count = len(runtime.emitter.traces)
    audit_count = len(manager.sync_log.entries)
    with pytest.raises(ValueError, match="already terminated"):
        runtime.changes.command_activate_project_role(
            role_assignment_id=role.role_assignment_id,
            reason="manual",
            triggered_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )
    assert len(runtime.emitter.traces) == trace_count
    assert len(manager.sync_log.entries) == audit_count
