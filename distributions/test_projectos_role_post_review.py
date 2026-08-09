from uuid import uuid4

import pytest

from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_post_review import (
    ProjectOSRoleEmergencyPostReview,
    ProjectOSRoleEmergencyPostReviewEvaluator,
)


def _request(*, emergency=True):
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference="activation:test",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=emergency,
    )


def test_emergency_without_review_remains_pending():
    request = _request()
    result = ProjectOSRoleEmergencyPostReviewEvaluator().evaluate(request)
    assert result["status"] == "pending"
    assert result["post_review_required"] is True
    assert result["post_review_completed"] is False
    assert result["historical_emergency_effect_preserved"] is True


def test_distinct_reviewer_can_confirm_emergency_afterwards():
    request = _request()
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="confirmed",
        reviewed_at="2026-08-09T00:10:00+00:00",
        comment="Notfallmaßnahme fachlich nachvollziehbar.",
    )
    result = ProjectOSRoleEmergencyPostReviewEvaluator(reviews=[review]).evaluate(request)
    assert result["status"] == "completed_confirmed"
    assert result["post_review_required"] is False
    assert result["post_review_completed"] is True
    assert result["escalation_required"] is False


def test_negative_review_creates_escalation_without_rewriting_history():
    request = _request()
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="negative",
        reviewed_at="2026-08-09T00:10:00+00:00",
    )
    result = ProjectOSRoleEmergencyPostReviewEvaluator(reviews=[review]).evaluate(request)
    assert result["status"] == "completed_negative"
    assert result["escalation_required"] is True
    assert result["historical_emergency_effect_preserved"] is True


def test_requester_cannot_review_own_emergency_action():
    request = _request()
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=request.requested_by_user_id,
        result="confirmed",
        reviewed_at="2026-08-09T00:10:00+00:00",
    )
    with pytest.raises(ValueError, match="different reviewer"):
        ProjectOSRoleEmergencyPostReviewEvaluator(reviews=[review]).evaluate(request)


def test_post_review_is_invalid_when_emergency_review_is_not_open():
    request = _request(emergency=False)
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="confirmed",
        reviewed_at="2026-08-09T00:10:00+00:00",
    )
    with pytest.raises(ValueError, match="emergency_pending_review"):
        ProjectOSRoleEmergencyPostReviewEvaluator(reviews=[review]).evaluate(request)
