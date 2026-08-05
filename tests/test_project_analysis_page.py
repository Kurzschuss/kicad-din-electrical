from tools.z_cockpit.project_analysis import AnalysisFinding, ProjectAnalysisResult
from tools.z_cockpit.project_analysis_page import project_analysis_page_html


def result(*findings: AnalysisFinding) -> ProjectAnalysisResult:
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    status = "error" if errors else "warning" if warnings else "ok"
    return ProjectAnalysisResult(
        device_count=3,
        symbol_count=2,
        checks_total=17,
        warning_count=warnings,
        error_count=errors,
        status=status,
        findings=findings,
    )


def test_project_analysis_page_groups_findings_and_shows_recommendations():
    html = project_analysis_page_html(result(
        AnalysisFinding(
            "footprint_missing",
            "error",
            "Z_Test:Schalter",
            "Zugeordnete Footprintdatei fehlt.",
            "Footprintdatei ergänzen.",
        ),
        AnalysisFinding(
            "footprint_missing",
            "warning",
            "Z_Test:Taster",
            "Footprintvorschau fehlt.",
            "Vorschau erzeugen.",
        ),
    ))

    assert 'id="page-diagnose"' in html
    assert "Projektanalyse" in html
    assert "Fehlende Footprints" in html
    assert "2 Befund(e) · 1 Fehler · 1 Warnung(en)" in html
    assert "Z_Test:Schalter" in html
    assert "Empfehlung:" in html
    assert "Footprintdatei ergänzen." in html


def test_project_analysis_page_shows_summary():
    html = project_analysis_page_html(result(
        AnalysisFinding("symbol_unused", "warning", "Z_Test:Frei", "Ungenutzt.", "Prüfen."),
    ))

    assert "Geräte geprüft<strong>3</strong>" in html
    assert "Symbole geprüft<strong>2</strong>" in html
    assert "Warnungen<strong>1</strong>" in html
    assert "Fehler<strong>0</strong>" in html
    assert "Status<strong>Warnung</strong>" in html


def test_project_analysis_page_reports_complete_project():
    html = project_analysis_page_html(result())

    assert "Keine Konsistenzprobleme gefunden." in html
    assert "Status<strong>OK</strong>" in html


def test_project_analysis_page_escapes_repository_data():
    html = project_analysis_page_html(result(
        AnalysisFinding(
            "custom<check>",
            "error",
            "<script>alert(1)</script>",
            "Fehler <kritisch>",
            "Datei & Zuordnung prüfen.",
        ),
    ))

    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Fehler &lt;kritisch&gt;" in html
    assert "Datei &amp; Zuordnung prüfen." in html
