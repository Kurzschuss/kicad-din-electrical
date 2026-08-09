from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from distributions.projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from distributions.projectos_role_deactivation_approval import ProjectOSApprovedRoleDeactivationEvaluator
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole


def _now():
    return datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)


def _setup():
    project_id = str(uuid4())
    principal = ProjectOSUserProfile("Projektleiter")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
        triggered_by_user_id=principal.user_id,
    )
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=user.user_id,
        reason="principal_returned",
        ended_at="2026-08-09T00:00:00+00:00",
        triggered_by_user_id=principal.user_id,
    )
    return project_id, principal, user, role, activation, deactivation


def test_high_risk_deactivation_without_approval_keeps_role_effective():
    project_id, _, user, role, activation, deactivation = _setup()
    evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
        roles=[role], activations=[activation], deactivations=[deactivation]
    )
    state = evaluator.state(project_id=project_id, user=user, at=_now(), risk_class="high")
    assignments = evaluator.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
        risk_class="high",
    )
    assert state["blocked_deactivations"][0]["approval"]["status"] == "approval_missing"
    assert len(state["effective_roles"]) == 1
    assert len(assignments) == 1


def test_approved_high_risk_deactivation_removes_role_effect():
    project_id, principal, user, role, activation, deactivation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{deactivation.deactivation_id}",
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-08T23:58:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-08T23:59:00+00:00",
    )
    evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
        roles=[role], activations=[activation], deactivations=[deactivation],
        approval_requests=[request], approvals=[approval],
    )
    state = evaluator.state(project_id=project_id, user=user, at=_now(), risk_class="high")
    assignments = evaluator.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
        risk_class="high",
    )
    assert state["approval_states"][0]["approval"]["status"] == "approved"
    assert state["effective_roles"] == []
    assert assignments == ()


def test_emergency_deactivation_is_effective_but_requires_post_review():
    project_id, principal, user, role, activation, deactivation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{deactivation.deactivation_id}",
        requested_by_user_id=principal.user_id,
        risk_class="critical",
        requested_at="2026-08-08T23:58:00+00:00",
        emergency=True,
    )
    evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
        roles=[role], activations=[activation], deactivations=[deactivation],
        approval_requests=[request], approvals=[],
    )
    state = evaluator.state(project_id=project_id, user=user, at=_now(), risk_class="critical")
    assert state["effective_roles"] == []
    assert state["pending_post_reviews"] == [deactivation.deactivation_id]
    assert state["approval_states"][0]["approval"]["status"] == "emergency_pending_review"


def test_rejected_deactivation_keeps_role_effective():
    project_id, principal, user, role, activation, deactivation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{deactivation.deactivation_id}",
        requested_by_user_id=principal.user_id,
        risk_class="critical",
        requested_at="2026-08-08T23:58:00+00:00",
    )
    rejection = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="reject",
        decided_at="2026-08-08T23:59:00+00:00",
    )
    evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
        roles=[role], activations=[activation], deactivations=[deactivation],
        approval_requests=[request], approvals=[rejection],
    )
    state = evaluator.state(project_id=project_id, user=user, at=_now(), risk_class="critical")
    assert state["approval_states"][0]["approval"]["status"] == "rejected"
    assert len(state["effective_roles"]) == 1
