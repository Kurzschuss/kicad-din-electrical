from pathlib import Path

from tools.project_validator import (
    ProjectCheckResult,
    ProjectValidationReport,
    _outdated_paths,
    validate_project,
)
from tools.z_cockpit.library_health_page import library_health_page_html


def test_project_validator_has_no_blocking_repository_errors():
    report = validate_project()
    assert report.checks_total == 10
    assert report.checks_passed == 10
    assert report.error_count == 0
    assert report.successful
    assert {item.check_id for item in report.checks} == {
        "PRJ-001",
        "PRJ-002",
        "PRJ-003",
        "PRJ-004",
        "PRJ-005",
        "PRJ-006",
        "PRJ-007",
        "PRJ-008",
        "PRJ-009",
        "PRJ-010",
    }


def test_project_validation_report_is_machine_readable():
    report = ProjectValidationReport(
        (
            ProjectCheckResult(
                "PRJ-TEST",
                "test",
                "Testprüfung",
                "warning",
                "Nur ein Hinweis.",
                ("Detail",),
            ),
        )
    )
    payload = report.to_dict()
    assert payload["schema_version"] == 1
    assert payload["status"] == "warning"
    assert payload["checks_total"] == 1
    assert payload["checks_passed"] == 1
    assert payload["warning_count"] == 1
    assert payload["error_count"] == 0
    assert payload["checks"][0]["check_id"] == "PRJ-TEST"


def test_outdated_paths_reports_only_drift(tmp_path: Path):
    current = tmp_path / "current.txt"
    stale = tmp_path / "stale.txt"
    current.write_text("aktuell\n", encoding="utf-8")
    stale.write_text("alt\n", encoding="utf-8")

    result = _outdated_paths({
        current: "aktuell\n",
        stale: "neu\n",
        tmp_path / "missing.txt": "erwartet\n",
    })

    assert str(stale) in result
    assert str(tmp_path / "missing.txt") in result
    assert str(current) not in result


def test_quality_page_can_render_project_validation_report():
    report = ProjectValidationReport(
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
                "Ein Hinweis bleibt offen.",
                ("<nicht ungefiltert ausgeben>",),
            ),
        )
    )

    html = library_health_page_html((), project_report=report)
    assert "Projektkonsistenz" in html
    assert 'data-check="PRJ-001"' in html
    assert 'data-status="warning"' in html
    assert "2/2" in html
    assert "Ein Hinweis bleibt offen." in html
    assert "<nicht ungefiltert ausgeben>" not in html
    assert "&lt;nicht ungefiltert ausgeben&gt;" in html
