"""Tests für kontextsensitive Folgeziele aus Z_Cockpit-Detailansichten."""
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_detail_actions import ZCockpitDetailActionsView
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_context import ZCockpitNavigationContext
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver


def _element(context, title, correlation_id):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=title,
        correlation_id=correlation_id,
    )


def test_knowledge_element_offers_origin_correlation_audit_and_related_knowledge():
    manager = DinEditorProjectManager()
    project_context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(project_context, "A", correlation_id))
    second = memory.add(_element(project_context, "B", correlation_id))
    memory.relate(first, second, "justifies")
    resolver = ZCockpitNavigationResolver(manager, memory=memory)
    nav = ZCockpitNavigationContext(ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        knowledge_ids=(first.knowledge_id,),
    ))

    state = ZCockpitDetailActionsView(resolver).state(nav)
    codes = [item["code"] for item in state["actions"]]

    assert "knowledge_origin" in codes
    assert "correlation" in codes
    assert "audit" in codes
    assert "knowledge_element" in codes
    related = next(item for item in state["actions"] if item["code"] == "knowledge_element")
    assert related["target"]["knowledge_ids"] == [second.knowledge_id]


def test_project_wide_knowledge_does_not_invent_correlation_actions():
    manager = DinEditorProjectManager()
    project_context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    item = memory.add(ProjectOSKnowledgeElement.from_project_context(
        project_context,
        knowledge_type="decision",
        title="Projektweit",
        content="Projektweit",
    ))
    resolver = ZCockpitNavigationResolver(manager, memory=memory)
    nav = ZCockpitNavigationContext(ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=manager.project_id,
        knowledge_ids=(item.knowledge_id,),
    ))

    state = ZCockpitDetailActionsView(resolver).state(nav)
    codes = {entry["code"] for entry in state["actions"]}

    assert "correlation" not in codes
    assert "audit" not in codes
    assert "knowledge_origin" in codes


def test_correlation_view_offers_audit_and_diagnostics_when_memory_exists():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    resolver = ZCockpitNavigationResolver(manager, memory=memory)
    nav = ZCockpitNavigationContext(ZCockpitNavigationTarget(
        view="correlation",
        project_id=manager.project_id,
        correlation_id=correlation_id,
    ))

    state = ZCockpitDetailActionsView(resolver).state(nav)
    codes = {entry["code"] for entry in state["actions"]}

    assert "audit" in codes
    assert "knowledge_diagnostics" in codes
    assert "project_overview" in codes


def test_detail_actions_are_read_only_and_keep_return_target():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    resolver = ZCockpitNavigationResolver(manager)
    overview = ZCockpitNavigationTarget(view="project_overview", project_id=manager.project_id)
    correlation = ZCockpitNavigationTarget(
        view="correlation",
        project_id=manager.project_id,
        correlation_id=correlation_id,
    )
    nav = ZCockpitNavigationContext(overview).push(correlation, current_label="Projektübersicht")
    before = manager.state()

    state = ZCockpitDetailActionsView(resolver).state(nav)

    assert state["read_only"] is True
    assert state["return_target"] == overview.as_dict()
    assert manager.state() == before
