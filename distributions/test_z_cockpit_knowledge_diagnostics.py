"""Tests für die Wissensgraph-Konsistenzdiagnose in Z_Cockpit."""
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


def _element(context, title, *, correlation_id=None, causation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
        causation_id=causation_id,
    )


def test_cockpit_exposes_graph_diagnostics_read_only():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    memory.add(_element(context, "Isoliertes Wissen"))

    before = manager.state()
    state = ZCockpitProjectCorrelationView(manager, memory=memory).state()

    diagnostics = state["memory"]["diagnostics"]
    assert diagnostics["available"] is True
    assert diagnostics["is_consistent"] is False
    assert diagnostics["issue_count"] == 1
    assert diagnostics["issues"][0]["code"] == "ISOLATED_KNOWLEDGE"
    assert manager.state() == before


def test_cockpit_diagnostics_resolve_known_message_and_correlation():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    message = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="event",
        name="knowledge.created",
        payload={},
    )
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(
        context,
        "Korrelierte Entscheidung",
        correlation_id=message.correlation_id,
        causation_id=message.message_id,
    ))
    second = memory.add(_element(context, "Nachweis"))
    memory.relate(first, second, "documented_in")

    state = ZCockpitProjectCorrelationView(manager, [message], memory).state()
    codes = {item["code"] for item in state["memory"]["diagnostics"]["issues"]}

    assert "UNRESOLVED_CAUSATION" not in codes
    assert "UNRESOLVED_CORRELATION" not in codes


def test_cockpit_diagnostics_flag_unresolved_references_when_message_context_exists():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    known = ProjectOSMessageEnvelope.from_project_context(
        context,
        message_type="event",
        name="known.event",
        payload={},
    )
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(
        context,
        "Nicht auflösbar",
        correlation_id=str(uuid4()),
        causation_id=str(uuid4()),
    ))
    second = memory.add(_element(context, "Bezug"))
    memory.relate(first, second, "documented_in")

    state = ZCockpitProjectCorrelationView(manager, [known], memory).state()
    codes = {item["code"] for item in state["memory"]["diagnostics"]["issues"]}

    assert "UNRESOLVED_CAUSATION" in codes
    assert "UNRESOLVED_CORRELATION" in codes
