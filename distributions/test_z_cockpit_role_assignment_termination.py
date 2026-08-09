from datetime import datetime, timezone
from uuid import uuid4

from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_role_assignment_termination import ZCockpitRoleAssignmentTerminationView


def _now():
    return datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)


def _setup(risk_class="high"):
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
        triggered_by_user_id=principal.user_id,
    )
    activation_request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=principal.user_id,
        risk_class=risk_class,
        requested_at="2026-08-09T11:00:00+00:00",
    )
    activation_approval = ProjectOSRoleActionApproval(
        action_id=activation_request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T11:01:00+00:00",
    )
    return project_id, user, role, activation, activation_request, activation_approval


def test_high_risk_candidate_simulation_shows_second_approval_and_lost_permission():
    project_id, user, role, activation, request, approval = _setup("high")
    view = ZCockpitRoleAssignmentTerminationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        approval_requests=[request],
        approvals=[approval],
        permission_map={"deputy": ["project.release"]},
        risk_class_map={"deputy": "high"},
    )

    state = view.simulate_candidate(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T12:00:00+00:00",
        at=_now(),
    )

    assert state["approval_action_type"] == "role_assignment_termination"
    assert state["approval_required"] is True
    assert state["would_be_effective_now_without_new_approval"] is False
    assert state["potential_lost_permissions"] == ["project.release"]
    assert state["next_action"] == "request_role_assignment_termination_approval"
    assert state["domain_mutation"] is False


def test_low_risk_candidate_can_be_effective_when_due_without_second_approval():
    project_id, user, role, activation, _, _ = _setup("low")
    view = ZCockpitRoleAssignmentTerminationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        permission_map={"deputy": ["project.read"]},
        risk_class_map={"deputy": "low"},
    )

    state = view.simulate_candidate(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T12:00:00+00:00",
        at=_now(),
    )

    assert state["approval_required"] is False
    assert state["would_be_effective_when_due_without_new_approval"] is True
    assert state["would_be_effective_now_without_new_approval"] is True
    assert state["next_action"] == "execute_termination"


def test_missing_risk_configuration_is_visible_and_fail_closed_in_simulation():
    project_id, user, role, activation, _, _ = _setup("low")
    view = ZCockpitRoleAssignmentTerminationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        permission_map={"deputy": ["project.read"]},
        risk_class_map={},
    )

    state = view.simulate_candidate(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T12:00:00+00:00",
        at=_now(),
    )

    assert state["status"] == "risk_not_configured"
    assert state["configuration_required"] is True
    assert state["would_be_effective_when_due_without_new_approval"] is False
    assert state["next_action"] == "configure_role_risk"
