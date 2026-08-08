"""Tests für die read-only Z_Cockpit-Sicht auf Wissensstatus."""
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_knowledge_status import ZCockpitKnowledgeStatusView


def _element(context, title, *, correlation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
    )


def test_cockpit_explains_superseded_knowledge_read_only():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    old = memory.add(_element(context, "Alte Entscheidung"))
    new = memory.add(_element(context, "Neue Entscheidung"))
    memory.relate(new, old, "supersedes")

    result = ZCockpitKnowledgeStatusView(memory).explain(old.knowledge_id)

    assert result["read_only"] is True
    assert result["graph_status"] == "superseded"
    assert "Neue Entscheidung" in result["status_text"]
    assert old.status == "active"


def test_cockpit_explains_conflict_without_claiming_replacement():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "Entscheidung A"))
    second = memory.add(_element(context, "Entscheidung B"))
    memory.relate(second, first, "refutes")

    result = ZCockpitKnowledgeStatusView(memory).explain(first.knowledge_id)

    assert result["graph_status"] == "conflicted"
    assert result["is_superseded"] is False
    assert "Entscheidung B" in result["status_text"]


def test_cockpit_status_respects_correlation_scope():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    target = memory.add(_element(context, "Vorgangsentscheidung", correlation_id=correlation_id))
    project_wide = memory.add(_element(context, "Projektweite Ablösung"))
    memory.relate(project_wide, target, "supersedes")

    result = ZCockpitKnowledgeStatusView(memory).explain(
        target.knowledge_id,
        correlation_id=correlation_id,
    )

    assert result["graph_status"] == "unchallenged"
    assert result["is_superseded"] is False
