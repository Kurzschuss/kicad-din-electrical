"""Tests für explizite, korrelierbare ProjectOS-Wissenselemente."""
from uuid import UUID, uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory


def test_knowledge_element_from_project_context_uses_stable_project_id():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)

    element = ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Recovery bleibt explizit",
        content="Recovery darf nicht automatisch den aktiven Projektstand ersetzen.",
        source="ADR/Implementierung",
    )

    assert element.project_id == manager.project_id
    UUID(element.knowledge_id)
    assert element.correlation_id is None
    assert element.causation_id is None


def test_knowledge_from_message_keeps_project_correlation_and_direct_cause():
    manager = DinEditorProjectManager()
    message = ProjectOSMessageEnvelope.from_project_context(
        DinEditorProjectContext.from_manager(manager),
        message_type="event",
        name="project.recovery.failed",
        payload={"reason": "validation"},
    )

    element = ProjectOSKnowledgeElement.from_message(
        message,
        knowledge_type="insight",
        title="Recovery-Validierung fehlgeschlagen",
        content="Ein formal lesbarer Recovery-Stand kann fachlich ungültig sein.",
        evidence_status="confirmed",
    )

    assert element.project_id == message.project_id
    assert element.correlation_id == message.correlation_id
    assert element.causation_id == message.message_id


def test_project_memory_accepts_only_elements_of_same_project():
    first = DinEditorProjectManager()
    second = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(first.project_id)

    own = ProjectOSKnowledgeElement.from_project_context(
        DinEditorProjectContext.from_manager(first),
        knowledge_type="insight",
        title="Eigene Erkenntnis",
        content="Gehört zum ersten Projekt.",
    )
    foreign = ProjectOSKnowledgeElement.from_project_context(
        DinEditorProjectContext.from_manager(second),
        knowledge_type="insight",
        title="Fremde Erkenntnis",
        content="Gehört zu einem anderen Projekt.",
    )

    memory.add(own)
    with pytest.raises(ValueError, match="another project"):
        memory.add(foreign)

    assert memory.state()["element_count"] == 1


def test_project_memory_filters_by_exact_correlation_id_without_inference():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    wanted = str(uuid4())
    other = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)

    memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Vorgang A",
        content="Explizit korreliertes Wissen.",
        correlation_id=wanted,
    ))
    memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Vorgang B",
        content="Anderer Vorgang.",
        correlation_id=other,
    ))
    memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="open_question",
        title="Projektweite Frage",
        content="Keine correlation_id vorhanden.",
    ))

    state = memory.state(correlation_id=wanted)

    assert state["filter"]["correlation_id"] == wanted
    assert state["element_count"] == 1
    assert state["elements"][0]["title"] == "Vorgang A"


def test_invalid_or_duplicate_knowledge_ids_are_rejected():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    knowledge_id = str(uuid4())

    element = ProjectOSKnowledgeElement(
        knowledge_type="insight",
        title="Erkenntnis",
        content="Explizites Wissen.",
        project_id=manager.project_id,
        knowledge_id=knowledge_id,
    )
    memory.add(element)

    with pytest.raises(ValueError, match="already exists"):
        memory.add(element)

    with pytest.raises(ValueError, match="knowledge_id must be a UUID"):
        ProjectOSKnowledgeElement(
            knowledge_type="insight",
            title="Fehlerhafte ID",
            content="Darf nicht akzeptiert werden.",
            project_id=manager.project_id,
            knowledge_id="keine-uuid",
        )
