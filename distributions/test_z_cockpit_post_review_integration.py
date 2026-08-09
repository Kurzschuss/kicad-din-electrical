from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTraceEmitter
from .z_cockpit_attention import ZCockpitAttentionView
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview
from .z_cockpit_role_approval_trace import ZCockpitRoleApprovalTraceView


def _request(project_id):
    return ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )


def _traces(project_id, result):
    request = _request(project_id)
    approval_trace = ProjectOSRoleApprovalTraceEmitter().emit(request)
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result=result,
        reviewed_at="2026-08-09T00:10:00+00:00",
        comment="Nachprüfung",
    )
    post_trace = ProjectOSRolePostReviewTraceEmitter().emit(
        approval_trace,
        request,
        reviews=[review],
    )
    return request, approval_trace, post_trace


def test_confirmed_post_review_closes_attention_and_trace_status():
    manager = DinEditorProjectManager()
    request, approval_trace, post_trace = _traces(manager.project_id, "confirmed")
    overview = ZCockpitProjectLeadOverview(manager, post_review_traces=[post_trace])
    attention = ZCockpitAttentionView(
        overview,
        approval_traces=[approval_trace],
        post_review_traces=[post_trace],
    ).state()
    detail = ZCockpitRoleApprovalTraceView(
        messages=post_trace.messages,
        audit_entries=post_trace.audit_entries,
    ).state(
        project_id=manager.project_id,
        correlation_id=post_trace.correlation_id,
        action_id=request.action_id,
    )

    assert detail["status"] == "completed_confirmed"
    assert detail["post_review_completed"] is True
    assert detail["attention_required"] is False
    assert all(item["code"] != "APPROVAL_EMERGENCY_POST_REVIEW" for item in attention["items"])
    assert overview.state()["post_reviews"]["confirmed_count"] == 1


def test_negative_post_review_remains_red_escalation():
    manager = DinEditorProjectManager()
    request, approval_trace, post_trace = _traces(manager.project_id, "negative")
    overview = ZCockpitProjectLeadOverview(manager, post_review_traces=[post_trace])
    attention = ZCockpitAttentionView(
        overview,
        approval_traces=[approval_trace],
        post_review_traces=[post_trace],
    ).state()
    detail = ZCockpitRoleApprovalTraceView(
        messages=post_trace.messages,
        audit_entries=post_trace.audit_entries,
    ).state(
        project_id=manager.project_id,
        correlation_id=post_trace.correlation_id,
        action_id=request.action_id,
    )

    assert detail["status"] == "completed_negative"
    assert detail["escalation_required"] is True
    assert detail["attention_required"] is True
    escalation = next(item for item in attention["items"] if item["code"] == "APPROVAL_POST_REVIEW_ESCALATED")
    assert escalation["traffic_light"] == "red"
    assert escalation["detail_target"]["view"] == "approval_trace"
    assert overview.state()["post_reviews"]["escalated_count"] == 1
    assert overview.state()["traffic_light"] == "red"
