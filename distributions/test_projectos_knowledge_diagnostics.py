"""Tests für die read-only Konsistenzdiagnose des ProjectOS-Wissensgraphen."""
from uuid import uuid4

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_knowledge_diagnostics import ProjectOSKnowledgeDiagnosticsService
from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory


def _element(context, title, *, correlation_id=None, causation_id=None):
    return ProjectOSKnowledgeElement.from_project_context(
        context,
        knowledge_type="decision",
        title=title,
        content=f"Inhalt: {title}",
        correlation_id=correlation_id,
        causation_id=causation_id,
    )


def test_diagnostics_reports_isolated_nodes_and_duplicate_semantic_relations():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A"))
    second = memory.add(_element(context, "B"))
    memory.add(_element(context, "Ohne Beziehung"))
    memory.relate(first, second, "justifies")
    memory.relate(first, second, "justifies")

    result = ProjectOSKnowledgeDiagnosticsService(memory).analyze()
    codes = {issue["code"] for issue in result["issues"]}

    assert result["is_consistent"] is False
    assert "ISOLATED_KNOWLEDGE" in codes
    assert "DUPLICATE_SEMANTIC_RELATION" in codes


def test_diagnostics_reports_supersession_cycle_and_ambiguity():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    memory = ProjectOSProjectMemory(manager.project_id)
    v1 = memory.add(_element(context, "V1"))
    v2 = memory.add(_element(context, "V2"))
    v3 = memory.add(_element(context, "V3"))
    v4 = memory.add(_element(context, "V4"))

    memory.relate(v2, v1, "supersedes")
    memory.relate(v3, v2, "supersedes")
    memory.relate(v1, v3, "supersedes")
    memory.relate(v4, v2, "supersedes")

    result = ProjectOSKnowledgeDiagnosticsService(memory).analyze()
    conflict = next(issue for issue in result["issues"] if issue["code"] == "SUPERSESSION_CONFLICT")

    assert conflict["count"] >= 1
    assert any(item["cycle"] for item in conflict["items"])


def test_diagnostics_reports_unresolved_message_and_correlation_references():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    correlation_id = str(uuid4())
    causation_id = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    memory.add(_element(context, "Referenziertes Wissen", correlation_id=correlation_id, causation_id=causation_id))

    result = ProjectOSKnowledgeDiagnosticsService(
        memory,
        known_message_ids={str(uuid4())},
        known_correlation_ids={str(uuid4())},
    ).analyze()
    codes = {issue["code"] for issue in result["issues"]}

    assert "UNRESOLVED_CAUSATION" in codes
    assert "UNRESOLVED_CORRELATION" in codes


def test_diagnostics_respects_correlation_scope_without_cross_scope_issues():
    manager = DinEditorProjectManager()
    context = DinEditorProjectContext.from_manager(manager)
    wanted = str(uuid4())
    memory = ProjectOSProjectMemory(manager.project_id)
    first = memory.add(_element(context, "A", correlation_id=wanted))
    second = memory.add(_element(context, "B", correlation_id=wanted))
    project_wide = memory.add(_element(context, "Projektweit"))
    memory.relate(first, second, "justifies")
    memory.relate(second, project_wide, "causes")

    result = ProjectOSKnowledgeDiagnosticsService(memory).analyze(correlation_id=wanted)

    assert result["element_count"] == 2
    assert result["relation_count"] == 1
    assert result["is_consistent"] is True
