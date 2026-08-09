"""Tests für automatische, read-only Herkunftserklärungen im Z_Cockpit."""
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


def _element(context, knowledge_type, title, correlation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type=knowledge_type,
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
    )


def test_cockpit_finds_origin_root_without_known_source():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung"))
    decision = memory.add(_element(context, "decision", "Entscheidung"))
    implementation = memory.add(_element(context, "implementation_reference", "Implementierung"))
    test = memory.add(_element(context, "test_reference", "Test"))
    memory.relate(requirement, decision, "justifies")
    memory.relate(decision, implementation, "implemented_by")
    memory.relate(implementation, test, "tested_by")

    before = manager.state()
    result = ZCockpitProjectCorrelationView(manager, memory=memory).explain_knowledge_origin(test.knowledge_id)

    assert result["found"] is True
    assert result["read_only"] is True
    assert result["origin_count"] == 1
    assert result["origins"][0]["source_knowledge_id"] == requirement.knowledge_id
    assert [node["title"] for node in result["origins"][0]["nodes"]] == [
        "Anforderung", "Entscheidung", "Implementierung", "Test"
    ]
    assert manager.state() == before


def test_cockpit_reports_multiple_explicit_origins():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung"))
    risk = memory.add(_element(context, "risk", "Risiko"))
    decision = memory.add(_element(context, "decision", "Entscheidung"))
    memory.relate(requirement, decision, "justifies")
    memory.relate(risk, decision, "affects")

    result = ZCockpitProjectCorrelationView(manager, memory=memory).explain_knowledge_origin(decision.knowledge_id)

    assert result["origin_count"] == 2
    root_titles = {path["nodes"][0]["title"] for path in result["origins"]}
    assert root_titles == {"Anforderung", "Risiko"}


def test_origin_explanation_respects_correlation_scope():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung", correlation_id))
    decision = memory.add(_element(context, "decision", "Entscheidung", correlation_id))
    project_wide = memory.add(_element(context, "insight", "Projektweit"))
    memory.relate(requirement, decision, "justifies")
    memory.relate(project_wide, decision, "affects")

    result = ZCockpitProjectCorrelationView(manager, memory=memory).explain_knowledge_origin(
        decision.knowledge_id,
        correlation_id=correlation_id,
    )

    assert result["origin_count"] == 1
    assert result["origins"][0]["source_knowledge_id"] == requirement.knowledge_id
    with pytest.raises(ValueError, match="target knowledge element is not visible"):
        ZCockpitProjectCorrelationView(manager, memory=memory).explain_knowledge_origin(
            project_wide.knowledge_id,
            correlation_id=correlation_id,
        )


def test_origin_without_memory_does_not_invent_provenance():
    manager = DinEditorProjectManager()
    target_id = str(uuid4())

    result = ZCockpitProjectCorrelationView(manager).explain_knowledge_origin(target_id)

    assert result["found"] is False
    assert result["origin_count"] == 0
    assert result["origins"] == []
    assert result["read_only"] is True
