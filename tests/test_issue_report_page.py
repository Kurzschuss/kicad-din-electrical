import json
from pathlib import Path

from tools.validate_device_catalog import REPO_ROOT
from tools.z_cockpit import page_by_id
from tools.z_cockpit.diagnostics_page import DiagnosticEntry, DiagnosticsSnapshot
from tools.z_cockpit.issue_report_page import (
    IssueReportSnapshot,
    RepositoryReportState,
    collect_issue_report,
    issue_report_page_html,
    load_repository_report_state,
)
from tools.z_cockpit.project_model import MilestoneState, ProjectState
from tools.z_cockpit.security_status import SecurityItem


def _snapshot(*, repository_current: bool = True) -> IssueReportSnapshot:
    return IssueReportSnapshot(
        project_name="Testprojekt",
        target_release="1.0",
        projectos_version="0.80.0",
        diagnostics=(
            DiagnosticEntry(
                severity="warning",
                source="Projektvalidator",
                code="PRJ-002",
                area="Bibliotheken",
                reference="Testreferenz",
                message_de="Ein Testhinweis.",
                action_de="Prüfen.",
            ),
        ),
        diagnostic_error_count=0,
        diagnostic_warning_count=1,
        security_items=(
            SecurityItem("versionspruefung", "Versionsprüfung", "vorhanden", "Prüfung vorhanden"),
        ),
        repository=RepositoryReportState(
            available=True,
            status="original_aktuell" if repository_current else "lokal_veraendert",
            current=repository_current,
            message="Repositorystatus geprüft.",
            local_commit="abc123",
            branch="main",
            official_remote=True,
            clean_worktree=repository_current,
        ),
    )


def test_issue_report_page_is_registered_and_implemented() -> None:
    page = page_by_id("fehlerbericht")
    assert page.implemented is True
    assert page.label_de == "Fehler melden"


def test_issue_report_page_contains_preview_privacy_and_explicit_github_gate() -> None:
    html = issue_report_page_html(_snapshot())
    assert 'id="page-fehlerbericht"' in html
    assert "strukturierter Bericht und GitHub-Issue-Vorbereitung" in html
    assert 'id="issue-report-preview"' in html
    assert 'id="issue-confirm-review"' in html
    assert 'id="issue-report-github" disabled' in html
    assert "Passwörter, Tokens, Schlüssel" in html
    assert "Benutzer-/Berechtigungsbestände" in html
    assert "python -m tools.check_repository_version" in html
    assert "bug_report.yml" in html
    assert "PRJ-002" in html
    assert "Versionsprüfung" in html


def test_issue_report_page_keeps_github_gate_bound_to_repository_result() -> None:
    html = issue_report_page_html(_snapshot(repository_current=False))
    assert 'data-ready="false"' in html
    assert "GitHub-Meldung: gesperrt" in html
    assert "ctx.repository.current" in html


def test_repository_result_loader_ignores_authenticated_user(tmp_path: Path) -> None:
    path = tmp_path / "VERSIONSPRUEFUNG.json"
    path.write_text(
        json.dumps(
            {
                "status": "entwickler_freigegeben",
                "current": True,
                "message": "Freigegeben",
                "local_commit": "abc",
                "branch": "feature",
                "ahead": 1,
                "behind": 0,
                "official_remote": True,
                "clean_worktree": False,
                "developer_mode": True,
                "authenticated_user": "soll-nicht-in-den-report",
                "developer_authorized": True,
            }
        ),
        encoding="utf-8",
    )
    result = load_repository_report_state(path)
    assert result.current is True
    assert result.developer_authorized is True
    assert not hasattr(result, "authenticated_user")


def test_collect_issue_report_uses_injected_project_diagnostics_and_security(tmp_path: Path) -> None:
    version_path = tmp_path / "VERSIONSPRUEFUNG.json"
    version_path.write_text(
        json.dumps({"status": "original_aktuell", "current": True, "message": "Aktuell"}),
        encoding="utf-8",
    )
    diagnostics = DiagnosticsSnapshot(
        entries=(
            DiagnosticEntry(
                severity="error",
                source="Projektanalyse",
                code="ANL-test",
                area="Gerätekatalog",
                reference="device-x",
                message_de="Fehler",
                action_de="Korrigieren",
            ),
        ),
        project_checks_total=1,
        project_checks_passed=0,
        analysis_checks_total=1,
        analysis_checks_passed=0,
    )
    project = ProjectState(
        name="test",
        display_name="Testprojekt",
        language="de",
        phase="Entwicklung",
        target_release="2.0",
        milestones=(MilestoneState("m", "M", ()),),
    )
    snapshot = collect_issue_report(
        diagnostics=diagnostics,
        security_items=(SecurityItem("x", "X", "vorhanden", "OK"),),
        project=project,
        version_result_path=version_path,
    )
    assert snapshot.project_name == "Testprojekt"
    assert snapshot.target_release == "2.0"
    assert snapshot.diagnostic_error_count == 1
    assert snapshot.repository.current is True


def test_bug_report_issue_form_exists_and_requires_privacy_confirmation() -> None:
    path = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"
    text = path.read_text(encoding="utf-8")
    assert "Z_Cockpit-Fehlerbericht" in text
    assert "Datenschutz und Sicherheit" in text
    assert "required: true" in text
