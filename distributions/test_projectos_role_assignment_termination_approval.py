from datetime import datetime, timezone
from uuid import uuid4

from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_user_project_roles import ProjectOSUserProjectRole


def _now():
    return datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)


def _setup(role_type="deputy"):
    project_id = str(uuid4())
    principal = ProjectOSUserProfile("Projektleitung")
    user = ProjectOSUserProfile("Stellvertretung")
    approver = ProjectOSUserProfile("Freigabe")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type=role_type)
    termination = ProjectOSProjectRoleAssignmentTermination(
        role_assignment_id=role.role_assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=role.scope,
        ended_at="2026-08-09T12:00:00+00:00",
        ended_by_user_id=principal.user_id,
        reason="Projektfunktion beendet",
    )
    return project_id, principal, user, approver, role, termination


def test_low_risk_termination_is_effective_without_second_approval():
    project_id, _, user, _, role, termination = _setup()
    evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        risk_class_map={"deputy": "low"},
    )

    state = evaluator.state(project_id=project_id, user=user, at=_now())

    assert state["effective_terminations"][0]["termination_id"] == termination.termination_id
    assert state["termination_states"][0]["approval"]["status"] == "approved_not_required"
    assert state["configuration_required"] is False


def test_high_risk_termination_without_or_with_pending_approval_is_blocked():
    project_id, principal, user, _, role, termination = _setup()
    evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        risk_class_map={"deputy": "high"},
    )
    missing = evaluator.state(project_id=project_id, user=user, at=_now())
    assert missing["effective_terminations"] == []
    assert missing["blocked_terminations"][0]["approval"]["status"] == "approval_missing"

    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T11:58:00+00:00",
    )
    pending = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        approval_requests=[request],
        risk_class_map={"deputy": "high"},
    ).state(project_id=project_id, user=user, at=_now())
    assert pending["effective_terminations"] == []
    assert pending["blocked_terminations"][0]["approval"]["status"] == "pending_approval"


def test_high_risk_termination_needs_external_approval_and_self_approval_is_ignored():
    project_id, principal, user, approver, role, termination = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T11:58:00+00:00",
    )
    self_approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=principal.user_id,
        decision="approve",
        decided_at="2026-08-09T11:59:00+00:00",
    )
    self_state = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        approval_requests=[request],
        approvals=[self_approval],
        risk_class_map={"deputy": "high"},
    ).state(project_id=project_id, user=user, at=_now())
    assert self_state["effective_terminations"] == []
    assert self_state["blocked_terminations"][0]["approval"]["self_approval_ignored"] is True

    external_approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T11:59:30+00:00",
    )
    approved = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        approval_requests=[request],
        approvals=[self_approval, external_approval],
        risk_class_map={"deputy": "high"},
    ).state(project_id=project_id, user=user, at=_now())
    assert approved["effective_terminations"][0]["termination_id"] == termination.termination_id
    assert approved["termination_states"][0]["approval"]["status"] == "approved"


def test_rejected_high_risk_termination_remains_ineffective():
    project_id, principal, user, approver, role, termination = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=principal.user_id,
        risk_class="critical",
        requested_at="2026-08-09T11:58:00+00:00",
    )
    rejection = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="reject",
        decided_at="2026-08-09T11:59:00+00:00",
    )
    state = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        approval_requests=[request],
        approvals=[rejection],
        risk_class_map={"deputy": "critical"},
    ).state(project_id=project_id, user=user, at=_now())
    assert state["effective_terminations"] == []
    assert state["blocked_terminations"][0]["approval"]["status"] == "rejected"


def test_emergency_high_risk_termination_is_temporarily_effective_and_requires_review():
    project_id, principal, user, _, role, termination = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=principal.user_id,
        risk_class="critical",
        requested_at="2026-08-09T11:58:00+00:00",
        emergency=True,
    )
    state = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        approval_requests=[request],
        risk_class_map={"deputy": "critical"},
    ).state(project_id=project_id, user=user, at=_now())
    assert state["effective_terminations"][0]["termination_id"] == termination.termination_id
    assert state["pending_post_reviews"][0]["approval"]["status"] == "emergency_pending_review"


def test_missing_role_risk_configuration_is_fail_closed():
    project_id, _, user, _, role, termination = _setup()
    state = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
        roles=[role],
        terminations=[termination],
        risk_class_map={},
    ).state(project_id=project_id, user=user, at=_now())
    assert state["effective_terminations"] == []
    assert state["configuration_required"] is True
    assert state["blocked_terminations"][0]["approval"]["status"] == "risk_not_configured"
