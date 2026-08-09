"""Tests für gerichtete Wissenspfade und Herkunftserklärungen."""
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_knowledge_path import ProjectOSKnowledgePathService
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory


def _element(context, knowledge_type, title, correlation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type=knowledge_type,
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
    )


def test_find_path_returns_shortest_directed_typed_path():
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

    path = ProjectOSKnowledgePathService(memory).find_path(requirement.knowledge_id, test.knowledge_id)

    assert path["found"] is True
    assert path["hop_count"] == 3
    assert [node["title"] for node in path["nodes"]] == ["Anforderung", "Entscheidung", "Implementierung", "Test"]
    assert [relation["relation_type"] for relation in path["relations"]] == ["justifies", "implemented_by", "tested_by"]
    assert "--justifies--> Entscheidung" in path["explanation"]


def test_find_path_does_not_reverse_directed_relations():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung"))
    decision = memory.add(_element(context, "decision", "Entscheidung"))
    memory.relate(requirement, decision, "justifies")

    path = ProjectOSKnowledgePathService(memory).find_path(decision.knowledge_id, requirement.knowledge_id)

    assert path["found"] is False
    assert path["nodes"] == []
    assert path["relations"] == []
    assert path["explanation"] is None


def test_find_path_respects_exact_correlation_scope():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    other = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(_element(context, "requirement", "Anforderung", correlation_id))
    decision = memory.add(_element(context, "decision", "Entscheidung", correlation_id))
    foreign = memory.add(_element(context, "insight", "Andere Erkenntnis", other))
    memory.relate(requirement, decision, "justifies")
    memory.relate(decision, foreign, "causes")

    service = ProjectOSKnowledgePathService(memory)
    path = service.find_path(requirement.knowledge_id, decision.knowledge_id, correlation_id=correlation_id)

    assert path["found"] is True
    assert path["correlation_id"] == correlation_id
    with pytest.raises(ValueError, match="target knowledge element is not visible"):
        service.find_path(requirement.knowledge_id, foreign.knowledge_id, correlation_id=correlation_id)


def test_find_path_rejects_unknown_nodes_instead_of_inventing_path():
    manager = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(manager.project_id)
    service = ProjectOSKnowledgePathService(memory)

    with pytest.raises(ValueError, match="source knowledge element is not visible"):
        service.find_path(str(uuid4()), str(uuid4()))
