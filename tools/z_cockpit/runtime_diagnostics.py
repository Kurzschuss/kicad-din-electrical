from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from distributions.projectos_project_memory_persistence import (
    ProjectOSProjectMemoryState,
    load_project_memory_state,
)
from distributions.z_cockpit_diagnostics_worklist import ZCockpitDiagnosticsWorklistView

from .diagnostics_page import DiagnosticEntry, DiagnosticsSnapshot
import tools.z_cockpit.diagnostics_page as _diagnostics_page

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_MEMORY_PATH = REPO_ROOT / "build" / "PROJECTOS_RUNTIME_MEMORY.json"

# Die bestehende Diagnose-Seite kann Fehler/Warnungen. Laufzeitdiagnosen besitzen
# zusätzlich die fachlich neutrale Stufe "info". Diese bleibt im Gesamtstatus
# nicht blockierend und wird in der Tabelle als "Hinweis" dargestellt.
_diagnostics_page._SEVERITY_LABELS.setdefault("info", "Hinweis")
_diagnostics_page._SEVERITY_ORDER.setdefault("info", 2)


@dataclass(frozen=True)
class RuntimeDiagnosticsSnapshot:
    source_available: bool
    source_label: str
    project_id: str | None
    saved_at: str | None
    element_count: int
    relation_count: int
    entries: tuple[DiagnosticEntry, ...]

    @property
    def issue_count(self) -> int:
        return len(self.entries)


def _details(issue: dict, state: ProjectOSProjectMemoryState) -> tuple[str, ...]:
    affected = issue.get("affected", {})
    lines = [
        f"Persistierter Stand: {state.saved_at}",
        f"Wissensknoten: {state.element_count}",
        f"Beziehungen: {state.relation_count}",
    ]
    for label, key in (
        ("Wissens-IDs", "knowledge_ids"),
        ("Beziehungs-IDs", "relation_ids"),
        ("Correlation-IDs", "correlation_ids"),
        ("Causation-IDs", "causation_ids"),
    ):
        values = tuple(str(value) for value in affected.get(key, ()) if value)
        if values:
            lines.append(f"{label}: {', '.join(values)}")
    return tuple(lines)


def _entry(issue: dict, state: ProjectOSProjectMemoryState) -> DiagnosticEntry:
    affected = issue.get("affected", {})
    references = tuple(str(value) for value in affected.get("knowledge_ids", ()) if value)
    reference = references[0] if references else state.project_id
    severity = str(issue.get("severity") or "info")
    return DiagnosticEntry(
        severity=severity,
        source="Laufzeitdiagnose",
        code=f"RT-{issue['code']}",
        area="Wissensgraph",
        reference=reference,
        message_de=str(issue.get("summary") or f"{issue.get('count', 0)} Laufzeitbefund(e) für {issue['code']}."),
        action_de=str(issue.get("recommended_action") or "Befund fachlich prüfen."),
        details=_details(issue, state),
    )


def collect_runtime_diagnostics(
    path: str | Path = DEFAULT_RUNTIME_MEMORY_PATH,
) -> RuntimeDiagnosticsSnapshot:
    """Lädt einen persistierten ProjectOS-Wissensgraphen und berechnet Diagnosen neu."""
    source = Path(path)
    if not source.is_file():
        return RuntimeDiagnosticsSnapshot(
            source_available=False,
            source_label=str(source),
            project_id=None,
            saved_at=None,
            element_count=0,
            relation_count=0,
            entries=(),
        )

    state = load_project_memory_state(source)
    worklist = ZCockpitDiagnosticsWorklistView(
        state.memory,
        known_message_ids=state.known_message_ids,
        known_correlation_ids=state.known_correlation_ids,
    ).state()
    entries = tuple(_entry(issue, state) for issue in worklist["work_items"])
    if not entries:
        entries = (
            DiagnosticEntry(
                severity="info",
                source="Laufzeitdiagnose",
                code="RT-OK",
                area="Wissensgraph",
                reference=state.project_id,
                message_de="Persistierter Wissensgraph ohne erkannte Strukturprobleme.",
                action_de="Keine Diagnosemaßnahme erforderlich.",
                details=(
                    f"Persistierter Stand: {state.saved_at}",
                    f"Wissensknoten: {state.element_count}",
                    f"Beziehungen: {state.relation_count}",
                ),
            ),
        )
    return RuntimeDiagnosticsSnapshot(
        source_available=True,
        source_label=str(source),
        project_id=state.project_id,
        saved_at=state.saved_at,
        element_count=state.element_count,
        relation_count=state.relation_count,
        entries=entries,
    )


def merge_runtime_diagnostics(
    base: DiagnosticsSnapshot,
    runtime: RuntimeDiagnosticsSnapshot | None = None,
) -> DiagnosticsSnapshot:
    """Führt persistierte Laufzeitbefunde mit den vorhandenen Repositorybefunden zusammen."""
    current = collect_runtime_diagnostics() if runtime is None else runtime
    if not current.source_available:
        return base
    entries = tuple(
        sorted(
            (*base.entries, *current.entries),
            key=lambda item: (
                _diagnostics_page._SEVERITY_ORDER.get(item.severity, 9),
                item.source.casefold(),
                item.area.casefold(),
                item.reference.casefold(),
                item.code.casefold(),
            ),
        )
    )
    return DiagnosticsSnapshot(
        entries=entries,
        project_checks_total=base.project_checks_total,
        project_checks_passed=base.project_checks_passed,
        analysis_checks_total=base.analysis_checks_total,
        analysis_checks_passed=base.analysis_checks_passed,
    )
