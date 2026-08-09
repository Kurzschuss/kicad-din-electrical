from uuid import uuid4

from .projectos_project_memory import ProjectOSProjectMemory
from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .projectos_role_knowledge_bridge import ProjectOSRoleKnowledgeBridge
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTraceEmitter


def _request(project_id=None):
    return ProjectOSRoleActionApprovalRequest(
        project_id=project_id or str(uuid4()),
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )


def test_bridge_materializes_referenced_approval_knowledge_without_new_truth():
    request = _request()
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request)
    memory = ProjectOSProjectMemory(request.project_id)

    created = ProjectOSRoleKnowledgeBridge(memory).materialize_approval_trace(trace)

    assert len(created) == 2
    assert all(item.knowledge_type == "approval" for item in created)
    assert created[0].metadata["action_id"] == request.action_id
    assert created[0].metadata["correlation_id"] == trace.correlation_id
    assert created[-1].metadata["truth_source"] == "ProjectOSRoleActionApprovalEvaluator"
    relations = memory.relations(relation_type="derived_from")
    assert len(relations) == 1
    assert relations[0].source_knowledge_id == created[-1].knowledge_id
    assert relations[0].target_knowledge_id == created[0].knowledge_id


def test_bridge_is_idempotent_for_same_approval_trace():
    request = _request()
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request)
    memory = ProjectOSProjectMemory(request.project_id)
    bridge = ProjectOSRoleKnowledgeBridge(memory)

    first = bridge.materialize_approval_trace(trace)
    second = bridge.materialize_approval_trace(trace)

    assert len(first) == 2
    assert second == ()
    assert len(memory.elements()) == 2


def test_post_review_knowledge_is_derived_from_approval_evidence():
    request = _request()
    approval_trace = ProjectOSRoleApprovalTraceEmitter().emit(request)
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=str(uuid4()),
        result="negative",
        reviewed_at="2026-08-09T00:10:00+00:00",
        comment="Nachprüfung negativ",
    )
    post_trace = ProjectOSRolePostReviewTraceEmitter().emit(
        approval_trace, request, reviews=[review]
    )
    memory = ProjectOSProjectMemory(request.project_id)
    bridge = ProjectOSRoleKnowledgeBridge(memory)
    bridge.materialize_approval_trace(approval_trace)

    created = bridge.materialize_post_review_trace(post_trace)

    assert len(created) == 1
    element = created[0]
    assert element.knowledge_type == "review_result"
    assert element.metadata["review_id"] == review.review_id
    assert element.metadata["escalation_required"] is True
    assert element.metadata["historical_emergency_effect_preserved"] is True
    assert element.metadata["truth_source"] == "ProjectOSRoleEmergencyPostReviewEvaluator"
    relations = memory.relations(knowledge_id=element.knowledge_id, relation_type="derived_from")
    assert len(relations) == 1


def test_bridge_rejects_foreign_project_trace():
    request = _request()
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request)
    memory = ProjectOSProjectMemory(str(uuid4()))

    try:
        ProjectOSRoleKnowledgeBridge(memory).materialize_approval_trace(trace)
    except ValueError as exc:
        assert "another project" in str(exc)
    else:
        raise AssertionError("foreign project trace must be rejected")
