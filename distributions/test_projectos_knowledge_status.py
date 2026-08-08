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
