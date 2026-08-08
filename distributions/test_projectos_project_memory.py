"""Tests für explizite, korrelierbare ProjectOS-Wissenselemente und Beziehungen."""
from uuid import UUID, uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import (
    ProjectOSKnowledgeElement,
    ProjectOSKnowledgeRelation,
    ProjectOSProjectMemory,
)


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


def test_memory_creates_typed_relation_between_existing_elements():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="requirement",
        title="Recovery muss explizit sein",
        content="Automatisches Fallback ist nicht zulässig.",
    ))
    decision = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Expliziter Recovery-Befehl",
        content="Recovery wird ausschließlich bewusst ausgelöst.",
    ))

    relation = memory.relate(requirement, decision, "justifies")

    assert relation.project_id == manager.project_id
    assert relation.source_knowledge_id == requirement.knowledge_id
    assert relation.target_knowledge_id == decision.knowledge_id
    assert relation.relation_type == "justifies"
    UUID(relation.relation_id)
    assert memory.state()["relation_count"] == 1


def test_relation_requires_existing_endpoints_and_same_project():
    first = DinEditorProjectManager()
    second = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(first.project_id)
    source = memory.add(ProjectOSKnowledgeElement.from_project_context(
        DinEditorProjectContext.from_manager(first),
        knowledge_type="decision",
        title="Entscheidung",
        content="Vorhandener Knoten.",
    ))
    missing_id = str(uuid4())

    with pytest.raises(ValueError, match="target does not exist"):
        memory.relate(source.knowledge_id, missing_id, "implemented_by")

    foreign_relation = ProjectOSKnowledgeRelation(
        relation_type="affects",
        project_id=second.project_id,
        source_knowledge_id=source.knowledge_id,
        target_knowledge_id=missing_id,
    )
    with pytest.raises(ValueError, match="another project"):
        memory.add_relation(foreign_relation)


def test_relation_rejects_unknown_type_self_reference_and_duplicate_id():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context, knowledge_type="decision", title="A", content="A"
    ))
    second = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context, knowledge_type="test_reference", title="B", content="B"
    ))

    with pytest.raises(ValueError, match="unsupported relation_type"):
        memory.relate(first, second, "irgendwie")

    with pytest.raises(ValueError, match="cannot target itself"):
        ProjectOSKnowledgeRelation(
            relation_type="confirms",
            project_id=manager.project_id,
            source_knowledge_id=first.knowledge_id,
            target_knowledge_id=first.knowledge_id,
        )

    relation = memory.relate(first, second, "tested_by")
    with pytest.raises(ValueError, match="relation_id already exists"):
        memory.add_relation(relation)


def test_correlation_filter_only_returns_relations_between_visible_elements():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    requirement = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="requirement",
        title="Anforderung",
        content="Korrelierte Anforderung.",
        correlation_id=correlation_id,
    ))
    decision = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title="Entscheidung",
        content="Korrelierte Entscheidung.",
        correlation_id=correlation_id,
    ))
    project_wide = memory.add(ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="insight",
        title="Projektweit",
        content="Nicht vorgangskorreliert.",
    ))
    memory.relate(requirement, decision, "justifies")
    memory.relate(decision, project_wide, "causes")

    state = memory.state(correlation_id=correlation_id)

    assert state["element_count"] == 2
    assert state["relation_count"] == 1
    assert state["relations"][0]["relation_type"] == "justifies"
