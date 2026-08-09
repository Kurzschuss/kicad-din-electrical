"""Tests für den read-only Z_Cockpit-Aufmerksamkeitsblock."""
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_sync_log import DinSyncLog
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .z_cockpit_attention import ZCockpitAttentionView
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


def _element(context, title, *, correlation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
    )


def test_attention_prioritizes_red_knowledge_issue_first():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    v4 = memory.add(_element(context, "V4"))
    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v2, "supersedes")
    memory.relate(v1, v3, "supersedes")
    memory.relate(v4, v2, "supersedes")

    view = ZCockpitAttentionView(ZCockpitProjectLeadOverview(manager, memory=memory))
    result = view.state()

    assert result["attention_required"] is True
    assert result["top_item"]["code"] == "SUPERSESSION_CONFLICT"
    assert result["top_item"]["traffic_light"] == "red"
    assert result["top_item"]["detail_target"]["view"] == "knowledge_diagnostics"


def test_attention_preserves_single_affected_correlation_for_detail_target():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    message = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="event",
        name="test.event",
        correlation_id=correlation_id,
        payload={},
    )
    memory = ProjectOSProjectMemory(manager.project_id)
    memory.add(_element(context, "Isoliert", correlation_id=correlation_id))

    result = ZCockpitAttentionView(
        ZCockpitProjectLeadOverview(manager, messages=[message], memory=memory)
    ).state()

    isolated = next(item for item in result["items"] if item["code"] == "ISOLATED_KNOWLEDGE")
    assert isolated["correlation_id"] == correlation_id
    assert isolated["detail_target"]["correlation_id"] == correlation_id


def test_pending_approval_appears_with_direct_approval_trace_target():
    manager = DinEditorProjectManager()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=manager.project_id,
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter(DinSyncLog()).emit(
        request, correlation_id=str(uuid4())
    )

    result = ZCockpitAttentionView(
        ZCockpitProjectLeadOverview(manager),
        approval_traces=[trace],
    ).state()

    item = next(item for item in result["items"] if item["code"] == "APPROVAL_PENDING")
    assert item["source"] == "approval"
    assert item["detail_target"]["view"] == "approval_trace"
    assert item["detail_target"]["metadata"]["action_id"] == request.action_id
    assert item["correlation_id"] == trace.correlation_id


def test_emergency_post_review_is_red_and_highest_priority():
    manager = DinEditorProjectManager()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=manager.project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )
    trace = ProjectOSRoleApprovalTraceEmitter(DinSyncLog()).emit(
        request, correlation_id=str(uuid4())
    )

    result = ZCockpitAttentionView(
        ZCockpitProjectLeadOverview(manager),
        approval_traces=[trace],
    ).state()

    assert result["traffic_light"] == "red"
    assert result["top_item"]["code"] == "APPROVAL_EMERGENCY_POST_REVIEW"
    assert result["top_item"]["priority"] == 30


def test_attention_is_empty_for_clean_project_and_read_only():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A"))
    second = memory.add(_element(context, "B"))
    memory.relate(first, second, "justifies")
    before = manager.state()

    result = ZCockpitAttentionView(ZCockpitProjectLeadOverview(manager, memory=memory)).state()

    assert result["attention_required"] is False
    assert result["attention_count"] == 0
    assert result["top_item"] is None
    assert result["read_only"] is True
    assert manager.state() == before
