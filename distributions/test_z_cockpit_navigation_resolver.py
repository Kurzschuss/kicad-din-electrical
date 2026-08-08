"""Tests für die read-only Auflösung von Z_Cockpit-Navigationszielen."""
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver


def _element(context, title, *, correlation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
    )


def test_resolver_rejects_target_for_other_project():
    manager = DinEditorProjectManager()
    resolver = ZCockpitNavigationResolver(manager)
    target = ZCockpitNavigationTarget(view="project_overview", project_id=str(uuid4()))

    with pytest.raises(ValueError, match="another project"):
        resolver.resolve(target)


def test_resolver_opens_correlation_and_filtered_audit():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    message = ProjectOSMessageEnvelope(
        message_type="event",
        name="project.changed",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        payload={},
    )
    manager.sync_log.entries.append({
        "project_id": manager.project_id,
        "correlation_id": correlation_id,
        "causation_id": str(uuid4()),
        "action": "test",
    })
    resolver = ZCockpitNavigationResolver(manager, messages=[message])

    correlation = resolver.resolve(ZCockpitNavigationTarget(
        view="correlation",
        project_id=manager.project_id,
        correlation_id=correlation_id,
    ))
    audit = resolver.resolve(ZCockpitNavigationTarget(
        view="audit",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        audit_filter="unresolved_causation",
    ))

    assert correlation["payload"]["filter"]["correlation_id"] == correlation_id
    assert audit["payload"]["entry_count"] == 1
    assert audit["payload"]["applied_filter"] == "unresolved_causation"


def test_resolver_opens_knowledge_element_path_and_origin():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "Anforderung", correlation_id=correlation_id))
    second = memory.add(_element(context, "Entscheidung", correlation_id=correlation_id))
    memory.relate(first, second, "justifies")
    resolver = ZCockpitNavigationResolver(manager, memory=memory)

    element = resolver.resolve(ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        knowledge_ids=(second.knowledge_id,),
    ))
    path = resolver.resolve(ZCockpitNavigationTarget(
        view="knowledge_path",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        knowledge_ids=(first.knowledge_id, second.knowledge_id),
    ))
    origin = resolver.resolve(ZCockpitNavigationTarget(
        view="knowledge_origin",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        knowledge_ids=(second.knowledge_id,),
    ))

    assert element["payload"]["element"]["knowledge_id"] == second.knowledge_id
    assert path["payload"]["found"] is True
    assert path["payload"]["hop_count"] == 1
    assert origin["payload"]["found"] is True
    assert origin["payload"]["origin_count"] == 1


def test_resolver_requires_memory_for_knowledge_targets():
    manager = DinEditorProjectManager()
    resolver = ZCockpitNavigationResolver(manager)
    target = ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=manager.project_id,
        knowledge_ids=(str(uuid4()),),
    )

    with pytest.raises(ValueError, match="requires project memory"):
        resolver.resolve(target)


def test_navigation_contract_requires_exact_knowledge_counts():
    project_id = str(uuid4())
    with pytest.raises(ValueError, match="exactly two"):
        ZCockpitNavigationTarget(
            view="knowledge_path",
            project_id=project_id,
            knowledge_ids=(str(uuid4()),),
        )
    with pytest.raises(ValueError, match="exactly one"):
        ZCockpitNavigationTarget(
            view="knowledge_origin",
            project_id=project_id,
            knowledge_ids=(str(uuid4()), str(uuid4())),
        )


def test_resolver_recovery_is_read_only_and_validates_optional_path():
    manager = DinEditorProjectManager()
    resolver = ZCockpitNavigationResolver(manager)
    state = resolver.resolve(ZCockpitNavigationTarget(
        view="recovery",
        project_id=manager.project_id,
    ))

    assert state["read_only"] is True
    assert state["payload"]["available"] is False

    with pytest.raises(ValueError, match="does not match"):
        resolver.resolve(ZCockpitNavigationTarget(
            view="recovery",
            project_id=manager.project_id,
            recovery_path="/tmp/fremd.recovery",
        ))
