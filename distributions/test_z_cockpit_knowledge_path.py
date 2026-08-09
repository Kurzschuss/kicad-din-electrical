"""Tests für Z_Cockpit-Herkunftserklärungen auf Basis expliziter Wissenspfade."""
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


def test_cockpit_explains_explicit_knowledge_path_read_only():
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
    result = ZCockpitProjectCorrelationView(manager, memory=memory).explain_knowledge_path(
        requirement.knowledge_id,
        test.knowledge_id,
    )

    assert result["found"] is True
    assert result["read_only"] is True
    assert result["hop_count"] == 3
    assert [node["title"] for node in result["nodes"]] == ["Anforderung", "Entscheidung", "Implementierung", "Test"]
    assert manager.state() == before


def test_cockpit_path_respects_correlation_scope_without_inference():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung", correlation_id))
    decision = memory.add(_element(context, "decision", "Entscheidung", correlation_id))
    project_wide = memory.add(_element(context, "insight", "Projektweite Erkenntnis"))
    memory.relate(requirement, decision, "justifies")
    memory.relate(decision, project_wide, "causes")

    view = ZCockpitProjectCorrelationView(manager, memory=memory)
    result = view.explain_knowledge_path(
        requirement.knowledge_id,
        decision.knowledge_id,
        correlation_id=correlation_id,
    )

    assert result["found"] is True
    assert result["correlation_id"] == correlation_id
    with pytest.raises(ValueError, match="target knowledge element is not visible"):
        view.explain_knowledge_path(
            requirement.knowledge_id,
            project_wide.knowledge_id,
            correlation_id=correlation_id,
        )


def test_cockpit_without_memory_reports_no_explanation_instead_of_inventing_one():
    manager = DinEditorProjectManager()
    source = str(uuid4())
    target = str(uuid4())

    result = ZCockpitProjectCorrelationView(manager).explain_knowledge_path(source, target)

    assert result["found"] is False
    assert result["nodes"] == []
    assert result["relations"] == []
    assert result["explanation"] is None
    assert result["read_only"] is True
