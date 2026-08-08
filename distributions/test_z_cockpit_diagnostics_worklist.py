"""Tests für die read-only Diagnose-Arbeitsansicht in Z_Cockpit."""
from uuid import uuid4

import pytest

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_diagnostics_worklist import ZCockpitDiagnosticsWorklistView


def _element(context, title, *, correlation_id=None, causation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
        causation_id=causation_id,
    )


def test_worklist_groups_error_as_red_and_warning_as_yellow():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    isolated = memory.add(_element(context, "Isoliert"))
    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v1, "supersedes")

    state = ZCockpitDiagnosticsWorklistView(memory).state(role="project_lead")

    assert state["traffic_light"] == "red"
    assert any(item["code"] == "SUPERSESSION_CONFLICT" for item in state["groups"]["red"])
    assert any(item["code"] == "ISOLATED_KNOWLEDGE" for item in state["groups"]["yellow"])
    assert state["read_only"] is True
    assert isolated.knowledge_id in next(
        item for item in state["groups"]["yellow"] if item["code"] == "ISOLATED_KNOWLEDGE"
    )["affected"]["knowledge_ids"]


def test_worklist_clean_graph_reports_green_without_fake_issue():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A"))
    second = memory.add(_element(context, "B"))
    memory.relate(first, second, "justifies")

    state = ZCockpitDiagnosticsWorklistView(memory).state()

    assert state["traffic_light"] == "green"
    assert state["issue_count"] == 0
    assert state["work_items"] == []
    assert state["groups"]["green"][0]["code"] == "NO_DIAGNOSTIC_ISSUES"


def test_worklist_exposes_role_specific_focus_without_changing_diagnostics():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    memory.add(_element(context, "Isoliert"))
    view = ZCockpitDiagnosticsWorklistView(memory)

    lead = view.state(role="project_lead")
    developer = view.state(role="developer")

    assert lead["role_label"] == "Projektleiter"
    assert developer["role_label"] == "Entwickler"
    assert lead["work_items"] == developer["work_items"]
    assert lead["role_focus"] != developer["role_focus"]


def test_worklist_respects_correlation_scope():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    wanted = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A", correlation_id=wanted))
    second = memory.add(_element(context, "B", correlation_id=wanted))
    memory.add(_element(context, "Projektweit isoliert"))
    memory.relate(first, second, "justifies")

    state = ZCockpitDiagnosticsWorklistView(memory).state(correlation_id=wanted)

    assert state["correlation_id"] == wanted
    assert state["traffic_light"] == "green"
    assert state["issue_count"] == 0


def test_worklist_rejects_unknown_role():
    manager = DinEditorProjectManager()
    memory = ProjectOSProjectMemory(manager.project_id)

    with pytest.raises(ValueError, match="unsupported diagnostics role"):
        ZCockpitDiagnosticsWorklistView(memory).state(role="admin")
