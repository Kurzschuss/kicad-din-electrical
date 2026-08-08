"""Tests für Breadcrumb- und Rücksprungkontext der Z_Cockpit-Navigation."""
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_context import ZCockpitBreadcrumb, ZCockpitNavigationContext
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver


def test_navigation_context_push_and_back_preserve_history():
    project_id = str(uuid4())
    overview = ZCockpitNavigationTarget(view="project_overview", project_id=project_id)
    correlation_id = str(uuid4())
    correlation = ZCockpitNavigationTarget(
        view="correlation",
        project_id=project_id,
        correlation_id=correlation_id,
    )
    knowledge_id = str(uuid4())
    element = ZCockpitNavigationTarget(
        view="knowledge_element",
        project_id=project_id,
        correlation_id=correlation_id,
        knowledge_ids=(knowledge_id,),
    )

    context = ZCockpitNavigationContext(current=overview)
    context = context.push(correlation, current_label="Projektübersicht")
    context = context.push(element, current_label="Vorgang")

    assert context.current == element
    assert context.return_target == correlation
    assert context.as_dict()["depth"] == 2
    assert [item["label"] for item in context.as_dict()["breadcrumbs"]] == ["Projektübersicht", "Vorgang"]

    back_once = context.back()
    assert back_once.current == correlation
    assert back_once.return_target == overview

    back_twice = back_once.back()
    assert back_twice.current == overview
    assert back_twice.return_target is None


def test_navigation_context_rejects_cross_project_breadcrumbs_and_pushes():
    first_project = str(uuid4())
    second_project = str(uuid4())
    current = ZCockpitNavigationTarget(view="project_overview", project_id=first_project)
    foreign = ZCockpitNavigationTarget(view="project_overview", project_id=second_project)

    with pytest.raises(ValueError, match="another project"):
        ZCockpitNavigationContext(
            current=current,
            breadcrumbs=(ZCockpitBreadcrumb("Fremd", foreign),),
        )

    context = ZCockpitNavigationContext(current=current)
    with pytest.raises(ValueError, match="another project"):
        context.push(foreign, current_label="Projektübersicht")


def test_navigation_resolver_preserves_breadcrumb_and_return_context():
    manager = DinEditorProjectManager()
    overview = ZCockpitNavigationTarget(
        view="project_overview",
        project_id=manager.project_id,
    )
    current = ZCockpitNavigationTarget(
        view="audit",
        project_id=manager.project_id,
        audit_filter="all",
    )
    context = ZCockpitNavigationContext(current=overview).push(
        current,
        current_label="Projektübersicht",
    )

    resolved = ZCockpitNavigationResolver(manager).resolve_context(context)

    assert resolved["resolved_view"] == "audit"
    assert resolved["navigation"]["depth"] == 1
    assert resolved["navigation"]["breadcrumbs"][0]["label"] == "Projektübersicht"
    assert resolved["navigation"]["return_target"]["view"] == "project_overview"
    assert resolved["read_only"] is True


def test_navigation_context_back_at_root_is_stable():
    target = ZCockpitNavigationTarget(view="project_overview", project_id=str(uuid4()))
    context = ZCockpitNavigationContext(current=target)

    assert context.back() is context
