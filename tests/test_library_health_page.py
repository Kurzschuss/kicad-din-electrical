from tools.z_cockpit.library_health_page import library_health_page_html
from tools.z_cockpit.quality_engine import LibraryQualityResult, QualityIssue


def test_library_health_page_contains_summary_and_issue_details():
    result = LibraryQualityResult(
        library_name="Z_Test",
        score=80,
        status="warning",
        checks_total=5,
        checks_passed=4,
        warning_count=1,
        error_count=0,
        issues=(
            QualityIssue(
                check_id="footprint_preview",
                severity="warning",
                message_de="Footprintvorschau fehlt.",
                symbol_reference="Z_Test:Schalter",
            ),
        ),
    )
    html = library_health_page_html((result,))
    assert 'id="page-qualitaet"' in html
    assert "Bibliotheksgesundheit" in html
    assert "Gesundheitswert" in html
    assert 'data-library="Z_Test"' in html
    assert 'data-status="warning"' in html
    assert 'aria-valuenow="80"' in html
    assert "4 von 5 Prüfungen bestanden" in html
    assert "Z_Test:Schalter" in html
    assert "Footprintvorschau fehlt." in html


def test_start_and_quality_headers_use_compact_top_spacing():
    html = library_health_page_html(())
    assert '#page-start>h2,#page-qualitaet>h2{margin:0 0 .25rem}' in html
    assert '#page-start>p,#page-qualitaet>p{margin:.1rem 0 .75rem}' in html
    assert '#page-qualitaet>.project-validation>h3{margin:.15rem 0 .25rem}' in html


def test_library_health_page_shows_complete_state():
    result = LibraryQualityResult(
        library_name="Z_OK",
        score=100,
        status="ok",
        checks_total=5,
        checks_passed=5,
        warning_count=0,
        error_count=0,
        issues=(),
    )
    html = library_health_page_html((result,))
    assert "100 % · OK" in html
    assert "Alle Qualitätsprüfungen bestanden." in html


def test_library_health_page_handles_empty_results():
    html = library_health_page_html(())
    assert "100 %" in html
    assert "0/0" in html


def test_library_health_page_escapes_engine_data():
    result = LibraryQualityResult(
        library_name="<library>",
        score=0,
        status="error",
        checks_total=1,
        checks_passed=0,
        warning_count=0,
        error_count=1,
        issues=(
            QualityIssue(
                check_id="<check>",
                severity="error",
                message_de="<script>",
                symbol_reference="<symbol>",
            ),
        ),
    )
    html = library_health_page_html((result,))
    assert "<script>" not in html
    assert "&lt;library&gt;" in html
    assert "&lt;check&gt;" in html
    assert "&lt;symbol&gt;" in html
