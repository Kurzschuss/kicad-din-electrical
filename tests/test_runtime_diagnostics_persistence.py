from uuid import uuid4

from distributions.projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from distributions.projectos_project_memory_persistence import save_project_memory_state
from tools.z_cockpit import DiagnosticsSnapshot, diagnostics_page_html
from tools.z_cockpit.runtime_diagnostics import collect_runtime_diagnostics, merge_runtime_diagnostics


def _element(project_id: str, title: str):
    return ProjectOSKnowledgeElement(
        knowledge_type="decision",
        title=title,
        content=f"Inhalt {title}",
        project_id=project_id,
    )


def test_runtime_diagnostics_are_recomputed_from_persisted_project_memory(tmp_path):
    project_id = str(uuid4())
    memory = ProjectOSProjectMemory(project_id)
    first = memory.add(_element(project_id, "A"))
    second = memory.add(_element(project_id, "B"))
    isolated = memory.add(_element(project_id, "Isoliert"))
    memory.relate(first, second, "justifies")
    memory.relate(first, second, "justifies")
    path = tmp_path / "PROJECTOS_RUNTIME_MEMORY.json"
    save_project_memory_state(path, memory, saved_at="2026-08-10T18:30:00+00:00")

    runtime = collect_runtime_diagnostics(path)
    by_code = {item.code: item for item in runtime.entries}

    assert runtime.source_available is True
    assert runtime.project_id == project_id
    assert runtime.element_count == 3
    assert runtime.relation_count == 2
    assert "RT-DUPLICATE_SEMANTIC_RELATION" in by_code
    assert by_code["RT-DUPLICATE_SEMANTIC_RELATION"].severity == "warning"
    assert "RT-ISOLATED_KNOWLEDGE" in by_code
    assert by_code["RT-ISOLATED_KNOWLEDGE"].severity == "info"
    assert isolated.knowledge_id in " ".join(by_code["RT-ISOLATED_KNOWLEDGE"].details)


def test_runtime_diagnostics_missing_source_is_nonblocking(tmp_path):
    runtime = collect_runtime_diagnostics(tmp_path / "fehlt.json")
    assert runtime.source_available is False
    assert runtime.entries == ()


def test_runtime_diagnostics_merge_and_render_without_changing_repository_check_counts(tmp_path):
    project_id = str(uuid4())
    memory = ProjectOSProjectMemory(project_id)
    memory.add(_element(project_id, "Isoliert"))
    path = tmp_path / "runtime.json"
    save_project_memory_state(path, memory, saved_at="2026-08-10T18:45:00+00:00")
    runtime = collect_runtime_diagnostics(path)
    base = DiagnosticsSnapshot(
        entries=(),
        project_checks_total=10,
        project_checks_passed=10,
        analysis_checks_total=8,
        analysis_checks_passed=8,
    )

    merged = merge_runtime_diagnostics(base, runtime)
    html = diagnostics_page_html(base, runtime)

    assert merged.project_checks_total == 10
    assert merged.analysis_checks_total == 8
    assert any(item.source == "Laufzeitdiagnose" for item in merged.entries)
    assert "Laufzeitdiagnose" in html
    assert "RT-ISOLATED_KNOWLEDGE" in html
    assert "Hinweis" in html
    assert "Persistierter Stand: 2026-08-10T18:45:00+00:00" in html


def test_clean_persisted_runtime_graph_is_visible_as_nonblocking_status(tmp_path):
    project_id = str(uuid4())
    memory = ProjectOSProjectMemory(project_id)
    first = memory.add(_element(project_id, "A"))
    second = memory.add(_element(project_id, "B"))
    memory.relate(first, second, "justifies")
    path = tmp_path / "runtime.json"
    save_project_memory_state(path, memory)

    runtime = collect_runtime_diagnostics(path)

    assert runtime.source_available is True
    assert len(runtime.entries) == 1
    assert runtime.entries[0].code == "RT-OK"
    assert runtime.entries[0].severity == "info"
