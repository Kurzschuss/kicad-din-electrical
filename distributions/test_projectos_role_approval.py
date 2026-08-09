from uuid import uuid4

from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)


def _request(*, risk="high", emergency=False):
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference="activation:test",
        requested_by_user_id=str(uuid4()),
        risk_class=risk,
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=emergency,
    )


def test_high_risk_requires_second_person():
    request = _request(risk="high")
    result = ProjectOSRoleActionApprovalEvaluator().evaluate(request)
    assert result["status"] == "pending_approval"
    assert result["effective"] is False
    assert result["second_person_required"] is True


def test_distinct_approver_makes_high_risk_effective():
    request = _request(risk="critical")
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    result = ProjectOSRoleActionApprovalEvaluator([approval]).evaluate(request)
    assert result["status"] == "approved"
    assert result["effective"] is True
    assert result["external_approval_count"] == 1


def test_self_approval_does_not_satisfy_four_eyes():
    request = _request(risk="high")
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=request.requested_by_user_id,
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    result = ProjectOSRoleActionApprovalEvaluator([approval]).evaluate(request)
    assert result["status"] == "pending_approval"
    assert result["effective"] is False
    assert result["self_approval_ignored"] is True


def test_external_rejection_blocks_action():
    request = _request(risk="critical")
    rejection = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="reject",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    result = ProjectOSRoleActionApprovalEvaluator([rejection]).evaluate(request)
    assert result["status"] == "rejected"
    assert result["effective"] is False


def test_emergency_is_temporarily_effective_but_requires_post_review():
    request = _request(risk="critical", emergency=True)
    result = ProjectOSRoleActionApprovalEvaluator().evaluate(request)
    assert result["status"] == "emergency_pending_review"
    assert result["effective"] is True
    assert result["post_review_required"] is True


def test_low_risk_needs_no_second_approval():
    request = _request(risk="low")
    result = ProjectOSRoleActionApprovalEvaluator().evaluate(request)
    assert result["status"] == "approved_not_required"
    assert result["effective"] is True
    assert result["approval_required"] is False
