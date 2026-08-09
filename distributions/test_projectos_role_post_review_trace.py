from uuid import uuid4

from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTraceEmitter


def _request():
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )


def test_confirmed_post_review_extends_same_correlation_and_causation_chain():
    request = _request()
    base = ProjectOSRoleApprovalTraceEmitter().emit(request)
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="confirmed",
        reviewed_at="2026-08-09T00:05:00+00:00",
        comment="Notfallentscheidung nachvollziehbar.",
    )
    trace = ProjectOSRolePostReviewTraceEmitter().emit(base, request, reviews=[review])

    assert trace.correlation_id == base.correlation_id
    assert trace.messages[-1].name == "projectos.role_action.post_review_completed"
    assert trace.messages[-1].causation_id == base.messages[-1].message_id
    assert trace.messages[-1].payload["result"] == "confirmed"
    assert trace.audit_entries[-1]["action"] == "post_review_completed"
    assert trace.audit_entries[-1]["correlation_id"] == base.correlation_id
    assert trace.audit_entries[-1]["causation_id"] == base.messages[-1].message_id
    assert trace.post_review_state["status"] == "completed_confirmed"


def test_negative_post_review_emits_escalation_without_rewriting_history():
    request = _request()
    base = ProjectOSRoleApprovalTraceEmitter().emit(request)
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="negative",
        reviewed_at="2026-08-09T00:05:00+00:00",
    )
    trace = ProjectOSRolePostReviewTraceEmitter().emit(base, request, reviews=[review])

    assert trace.messages[-1].name == "projectos.role_action.post_review_escalated"
    assert trace.messages[-1].payload["escalation_required"] is True
    assert trace.messages[-1].payload["historical_emergency_effect_preserved"] is True
    assert trace.audit_entries[-1]["action"] == "post_review_escalated"
    assert trace.post_review_state["status"] == "completed_negative"
    assert trace.post_review_state["historical_emergency_effect_preserved"] is True


def test_open_post_review_adds_no_fake_completion_event():
    request = _request()
    base = ProjectOSRoleApprovalTraceEmitter().emit(request)
    trace = ProjectOSRolePostReviewTraceEmitter().emit(base, request)

    assert trace.messages == base.messages
    assert trace.audit_entries == base.audit_entries
    assert trace.post_review_state["status"] == "pending"


def test_trace_rejects_mismatched_action():
    request = _request()
    base = ProjectOSRoleApprovalTraceEmitter().emit(request)
    foreign = _request()

    try:
        ProjectOSRolePostReviewTraceEmitter().emit(base, foreign)
    except ValueError as exc:
        assert "another action_id" in str(exc)
    else:
        raise AssertionError("mismatched action_id must be rejected")
