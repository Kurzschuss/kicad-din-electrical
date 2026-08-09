from uuid import uuid4

from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .z_cockpit_role_post_review import ZCockpitRoleEmergencyPostReviewView


def _request():
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference="activation:test",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )


def test_pending_post_review_is_red_and_requires_attention():
    request = _request()
    result = ZCockpitRoleEmergencyPostReviewView().state(request)
    assert result["status"] == "pending"
    assert result["traffic_light"] == "red"
    assert result["attention_required"] is True
    assert result["read_only"] is True


def test_confirmed_post_review_closes_attention_without_rewriting_history():
    request = _request()
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="confirmed",
        reviewed_at="2026-08-09T00:10:00+00:00",
    )
    result = ZCockpitRoleEmergencyPostReviewView(reviews=[review]).state(request)
    assert result["status"] == "completed_confirmed"
    assert result["traffic_light"] == "green"
    assert result["attention_required"] is False
    assert result["historical_emergency_effect_preserved"] is True


def test_negative_post_review_stays_red_as_escalation():
    request = _request()
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="negative",
        reviewed_at="2026-08-09T00:10:00+00:00",
        comment="Notfallmaßnahme war nicht ausreichend begründet.",
    )
    result = ZCockpitRoleEmergencyPostReviewView(reviews=[review]).state(request)
    assert result["status"] == "completed_negative"
    assert result["traffic_light"] == "red"
    assert result["attention_required"] is True
    assert result["escalation_required"] is True
