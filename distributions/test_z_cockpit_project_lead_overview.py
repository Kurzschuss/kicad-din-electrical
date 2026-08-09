"""Tests für die read-only Z_Cockpit-Projektleiter-Gesamtübersicht."""
from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


def _element(context, title):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
    )


def test_project_lead_overview_is_green_for_clean_visible_memory_and_read_only():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A"))
    second = memory.add(_element(context, "B"))
    memory.relate(first, second, "justifies")

    before = manager.state()
    result = ZCockpitProjectLeadOverview(manager, memory=memory).state()

    assert result["traffic_light"] == "green"
    assert result["attention_required"] is False
    assert result["summary"]["knowledge_issue_count"] == 0
    assert result["read_only"] is True
    assert manager.state() == before


def test_project_lead_overview_is_red_for_supersession_conflict():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v1, "supersedes")

    result = ZCockpitProjectLeadOverview(manager, memory=memory).state()

    assert result["traffic_light"] == "red"
    assert result["attention_required"] is True
    assert result["diagnostics"]["red_count"] >= 1
    assert any("Fehlerdiagnose" in reason for reason in result["attention_reasons"])


def test_project_lead_overview_is_yellow_without_memory_instead_of_claiming_green():
    manager = DinEditorProjectManager()

    result = ZCockpitProjectLeadOverview(manager).state()

    assert result["traffic_light"] == "yellow"
    assert result["diagnostics"]["available"] is False
    assert result["attention_required"] is True
    assert any("nicht vollständig bewertbar" in reason for reason in result["attention_reasons"])


def test_project_lead_overview_exposes_recovery_audit_and_summary_sections():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A"))
    second = memory.add(_element(context, "B"))
    memory.relate(first, second, "justifies")

    result = ZCockpitProjectLeadOverview(manager, memory=memory).state()

    assert result["project"]["project_id"] == manager.project_id
    assert "recovery" in result
    assert "audit" in result
    assert "diagnostics" in result
    assert result["summary"]["audit_entry_count"] == 0
    assert result["summary"]["message_count"] == 0
