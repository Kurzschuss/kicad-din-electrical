from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator, ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole


def _now():
    return datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)


def _setup(role_type="deputy"):
    project_id = str(uuid4())
    trigger = ProjectOSUserProfile("Projektleiter")
    user = ProjectOSUserProfile("Stellvertretung", weight=950)
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type=role_type)
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
        triggered_by_user_id=trigger.user_id,
    )
    return project_id, trigger, user, role, activation


def test_high_risk_activation_without_approval_request_has_no_permission_effect():
    project_id, _, user, role, activation = _setup()
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role], activations=[activation], risk_class_map={"deputy": "high"}
    )

    state = evaluator.state(project_id=project_id, user=user, at=_now())
    assignments = evaluator.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
    )

    assert assignments == ()
    assert state["blocked_activations"][0]["approval"]["status"] == "approval_missing"


def test_high_risk_activation_with_pending_request_has_no_permission_effect():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role], activations=[activation], approval_requests=[request], risk_class_map={"deputy": "high"}
    )

    state = evaluator.state(project_id=project_id, user=user, at=_now())
    assert state["blocked_activations"][0]["approval"]["status"] == "pending_approval"
    assert evaluator.permission_assignments(
        project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_now()
    ) == ()


def test_distinct_approval_enables_high_risk_role_permissions():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role], activations=[activation], approval_requests=[request], approvals=[approval], risk_class_map={"deputy": "high"}
    )

    assignments = evaluator.permission_assignments(
        project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_now()
    )
    assert len(assignments) == 1
    assert assignments[0].risk_class == "high"
    assert assignments[0].metadata["approval_status"] == "approved"


def test_emergency_activation_is_effective_but_stays_pending_post_review():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role], activations=[activation], approval_requests=[request], risk_class_map={"deputy": "critical"}
    )

    state = evaluator.state(project_id=project_id, user=user, at=_now())
    assignments = evaluator.permission_assignments(
        project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_now()
    )
    assert len(assignments) == 1
    assert len(state["pending_post_reviews"]) == 1
    assert assignments[0].metadata["post_review_required"] is True


def test_approved_role_allow_still_cannot_override_explicit_deny():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    evaluator = ProjectOSApprovedRoleActivationEvaluator(
        roles=[role], activations=[activation], approval_requests=[request], approvals=[approval], risk_class_map={"deputy": "high"}
    )
    derived = evaluator.permission_assignments(
        project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_now()
    )
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id, permission="project.release", source_type="deny", effect="deny"
    )

    result = ProjectOSAuthorizationEvaluator(derived + (deny,)).evaluate(user, "project.release", at=_now())
    assert result["decision"] == "deny"
    assert result["allowed"] is False
    assert result["weight_used_for_decision"] is False
