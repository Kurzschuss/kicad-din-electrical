"""Tests für explizite Widerspruchs- und Ablöseketten im Projektgedächtnis."""
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_knowledge_status import ProjectOSKnowledgeStatusService
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory


def _element(context, title, *, correlation_id=None, status="active"):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
        status=status,
    )


def test_status_marks_element_superseded_only_by_explicit_incoming_relation():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    old = memory.add(_element(context, "Alte Entscheidung"))
    new = memory.add(_element(context, "Neue Entscheidung"))
    memory.relate(new, old, "supersedes")

    state = ProjectOSKnowledgeStatusService(memory).analyze(old.knowledge_id)

    assert state["declared_status"] == "active"
    assert state["graph_status"] == "superseded"
    assert state["is_superseded"] is True
    assert state["superseded_by"][0]["other"]["knowledge_id"] == new.knowledge_id
    assert old.status == "active"


def test_status_reports_explicit_contradiction_without_mutating_declared_status():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "Entscheidung A", status="confirmed"))
    second = memory.add(_element(context, "Entscheidung B"))
    memory.relate(second, first, "contradicts")

    state = ProjectOSKnowledgeStatusService(memory).analyze(first.knowledge_id)

    assert state["declared_status"] == "confirmed"
    assert state["graph_status"] == "conflicted"
    assert state["has_conflicts"] is True
    assert state["conflicts"][0]["relation"]["relation_type"] == "contradicts"


def test_status_respects_correlation_scope_without_cross_scope_inference():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    target = memory.add(_element(context, "Vorgangsentscheidung", correlation_id=correlation_id))
    project_wide = memory.add(_element(context, "Projektweite Ablösung"))
    memory.relate(project_wide, target, "supersedes")

    scoped = ProjectOSKnowledgeStatusService(memory).analyze(
        target.knowledge_id,
        correlation_id=correlation_id,
    )

    assert scoped["graph_status"] == "unchallenged"
    assert scoped["is_superseded"] is False


def test_status_rejects_invisible_or_unknown_target():
    manager = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(manager.project_id)

    with pytest.raises(ValueError, match="not visible"):
        ProjectOSKnowledgeStatusService(memory).analyze(str(uuid4()))


def test_status_resolves_multistep_supersession_to_unique_current_successor():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v2, "supersedes")

    state = ProjectOSKnowledgeStatusService(memory).analyze(v1.knowledge_id)

    assert state["graph_status"] == "superseded"
    assert state["terminal_successor_count"] == 1
    assert state["current_successor"]["knowledge_id"] == v3.knowledge_id
    assert [node["title"] for node in state["supersession_chains"][0]["nodes"]] == ["V1", "V2", "V3"]
    assert state["supersession_chains"][0]["hop_count"] == 2
    assert state["supersession_cycle_detected"] is False
    assert state["supersession_ambiguous"] is False


def test_status_marks_multiple_terminal_successors_as_ambiguous():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2a = memory.add(_element(context, "V2A"))
    v2b = memory.add(_element(context, "V2B"))
    memory.relate(v2a, v1, "supersedes")
    memory.relate(v2b, v1, "supersedes")

    state = ProjectOSKnowledgeStatusService(memory).analyze(v1.knowledge_id)

    assert state["graph_status"] == "supersession_conflict"
    assert state["terminal_successor_count"] == 2
    assert state["current_successor"] is None
    assert state["supersession_ambiguous"] is True


def test_status_detects_supersession_cycle_instead_of_looping():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v2, "supersedes")
    memory.relate(v1, v3, "supersedes")

    state = ProjectOSKnowledgeStatusService(memory).analyze(v1.knowledge_id)

    assert state["graph_status"] == "supersession_conflict"
    assert state["supersession_cycle_detected"] is True
    assert state["current_successor"] is None
    assert any(chain["cycle"] for chain in state["supersession_chains"])