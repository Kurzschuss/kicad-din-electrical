from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_knowledge_origin_evidence import ZCockpitKnowledgeOriginEvidenceView
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


def _approval_element(project_id, correlation_id, *, action_id, title="Freigabewirksamkeit"):
    message_id = str(uuid4())
    return ProjectOSKnowledgeElement(
        knowledge_type="approval",
        title=title,
        content="Referenzierter Freigabenachweis.",
        project_id=project_id,
        status="active",
        source="projectos_role_approval_trace",
        correlation_id=correlation_id,
        causation_id=message_id,
        evidence_status="referenced",
        metadata={
            "reference_id": f"approval-outcome:{action_id}:{message_id}",
            "action_id": action_id,
            "message_id": message_id,
            "correlation_id": correlation_id,
            "truth_source": "ProjectOSRoleActionApprovalEvaluator",
        },
    )


def test_origin_evidence_exposes_truth_source_and_approval_navigation():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    action_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    element = memory.add(_approval_element(manager.project_id, correlation_id, action_id=action_id))

    result = ZCockpitKnowledgeOriginEvidenceView(
        ZCockpitProjectCorrelationView(manager, memory=memory)
    ).state(element.knowledge_id, correlation_id=correlation_id)

    assert result["found"] is True
    assert result["evidence_reference_count"] == 1
    evidence = result["evidence_references"][0]
    assert evidence["action_id"] == action_id
    assert evidence["truth_source"] == "ProjectOSRoleActionApprovalEvaluator"
    assert evidence["correlation_id"] == correlation_id
    assert evidence["message_id"] == element.metadata["message_id"]
    assert evidence["navigation_target"]["view"] == "approval_trace"
    assert evidence["navigation_target"]["metadata"]["action_id"] == action_id
    assert result["read_only"] is True


def test_origin_evidence_does_not_invent_approval_reference_for_normal_knowledge():
    manager = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(manager.project_id)
    element = memory.add(ProjectOSKnowledgeElement(
        knowledge_type="decision",
        title="Normale Entscheidung",
        content="Kein Freigabenachweis.",
        project_id=manager.project_id,
    ))

    result = ZCockpitKnowledgeOriginEvidenceView(
        ZCockpitProjectCorrelationView(manager, memory=memory)
    ).state(element.knowledge_id)

    assert result["found"] is True
    assert result["evidence_reference_count"] == 0
    assert result["evidence_references"] == []


def test_navigation_resolver_uses_evidence_aware_origin_view():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    action_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    element = memory.add(_approval_element(manager.project_id, correlation_id, action_id=action_id))

    target = ZCockpitNavigationTarget(
        view="knowledge_origin",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        knowledge_ids=(element.knowledge_id,),
    )
    resolved = ZCockpitNavigationResolver(manager, memory=memory).resolve(target)

    assert resolved["resolved_view"] == "knowledge_origin"
    assert resolved["payload"]["evidence_reference_count"] == 1
    assert resolved["payload"]["evidence_references"][0]["navigation_target"]["view"] == "approval_trace"
