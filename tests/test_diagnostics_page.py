from tools.project_validator import ProjectCheckResult, ProjectValidationReport
from tools.z_cockpit.diagnostics_page import (
    DiagnosticEntry,
    DiagnosticsSnapshot,
    collect_diagnostics,
    diagnostics_page_html,
)
from tools.z_cockpit.quality_engine import LibraryQualityResult, QualityIssue


def _project_report() -> ProjectValidationReport:
    return ProjectValidationReport(
        (
            ProjectCheckResult(
                "PRJ-001",
                "project_state",
                "Projektmodell",
                "ok",
                "Projektmodell ist gültig.",
            ),
            ProjectCheckResult(
                "PRJ-002",
                "libraries",
                "KiCad-Bibliotheken",
                "warning",
                "Ein nicht blockierender Hinweis bleibt offen.",
                ("LIB-WARN-0001 Z_Test: Herstellerfeld fehlt.",),
            ),
            ProjectCheckResult(
                "PRJ-003",
                "device_catalog",
                "Gerätekatalog",
                "error",
                "Gerätekatalog enthält einen Fehler.",
                ("device.invalid: Symbolreferenz fehlt.",),
            ),
        )
    )


def _library_results() -> tuple[LibraryQualityResult, ...]:
    return (
        LibraryQualityResult(
            library_name="Z_Test",
            score=60,
            status="warning",
            checks_total=5,
            checks_passed=3,
            warning_count=2,
            error_count=0,
            issues=(
                QualityIssue(
                    "symbol_preview",
                    "warning",
                    "Symbolvorschau fehlt.",
                    "Z_Test:Test",
                ),
                QualityIssue(
                    "complete_preview_pair",
                    "warning",
                    "Vollständiges Vorschaupaar fehlt.",
                    "Z_Test:Test",
                ),
            ),
        ),
    )


def test_collect_diagnostics_combines_project_and_library_findings():
    snapshot = collect_diagnostics(
        project_report=_project_report(),
        library_results=_library_results(),
    )

    assert snapshot.project_checks_total == 3
    assert snapshot.project_checks_passed == 2
    assert snapshot.library_checks_total == 5
    assert snapshot.library_checks_passed == 3
    assert snapshot.error_count == 1
    assert snapshot.warning_count == 3
    assert snapshot.status == "error"
    assert snapshot.entries[0].code == "PRJ-003"
    assert any(item.code == "LIB-symbol_preview" for item in snapshot.entries)
    assert any(item.source == "Bibliotheksqualität" for item in snapshot.entries)


def test_diagnostics_page_contains_filters_table_and_fixed_inspector():
    snapshot = collect_diagnostics(
        project_report=_project_report(),
        library_results=_library_results(),
    )
    html = diagnostics_page_html(snapshot)

    assert 'id="page-diagnose"' in html
    assert 'id="diagnostic-overview"' in html
    assert 'id="diagnostic-filter-severity"' in html
    assert 'id="diagnostic-filter-source"' in html
    assert 'id="diagnostic-filter-area"' in html
    assert 'class="diagnostic-inspector"' in html
    assert 'id="diagnostic-inspector-content"' in html
    assert "ProjectOS-Projektvalidator" in html
    assert "Bibliotheks-Quality-Engine" in html
    assert "Read-only" in html
    assert "PRJ-003" in html
    assert "LIB-symbol_preview" in html
    assert "Empfohlene Aktion" in html


def test_diagnostics_page_escapes_messages_and_details():
    snapshot = DiagnosticsSnapshot(
        entries=(
            DiagnosticEntry(
                severity="warning",
                source="<Quelle>",
                code="TEST",
                area="<Bereich>",
                reference="<Referenz>",
                message_de="<script>alert(1)</script>",
                action_de="<Aktion>",
                details=("<Detail>",),
            ),
        ),
        project_checks_total=1,
        project_checks_passed=1,
        library_checks_total=0,
        library_checks_passed=0,
    )
    html = diagnostics_page_html(snapshot)

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;Quelle&gt;" in html
    assert "&lt;Detail&gt;" in html


def test_repository_diagnostics_are_read_only_and_renderable():
    snapshot = collect_diagnostics()
    assert snapshot.project_checks_total == 10
    assert snapshot.project_checks_passed == 10
    assert snapshot.library_checks_total >= snapshot.library_checks_passed
    html = diagnostics_page_html(snapshot)
    assert "Diagnose" in html
    assert "Laufzeit-Wissensgraphdiagnosen" in html
