from __future__ import annotations

from dataclasses import replace
import json
import subprocess

import pytest

from tools.check_repository_version import VersionResult
from tools.projectos_governance import bootstrap_admin
from tools.projectos_issue_reporting import (
    AutoReportGate,
    ReportIdentity,
    duplicate_summary,
    evaluate_auto_report_gate,
    read_report,
    report_fingerprint,
    submit_auto_report,
)
from tools.projectos_project_cli import create_project


REPORT = """# Fehlerbericht: Diagnose zeigt falschen Zustand

- Kategorie: Projektvalidator / Qualität
- Cockpit-Kontext: diagnose
- Technische Referenz: PRJ-010

## Beschreibung

Die Diagnose zeigt reproduzierbar einen falschen Zustand.
"""


def cp(args, code=0, out="", err=""):
    return subprocess.CompletedProcess(args=args, returncode=code, stdout=out, stderr=err)


def test_report_fingerprint_is_stable_for_same_category_reference_and_title(tmp_path):
    a = report_fingerprint(REPORT)
    b = report_fingerprint(REPORT.replace("reproduzierbar", "immer"))
    assert a == b
    assert len(a) == 64


def test_report_secret_scan_blocks_tokens(tmp_path):
    path = tmp_path / "report.md"
    path.write_text(REPORT + "\ntoken=github_pat_abcdefghijklmnopqrstuv\n", encoding="utf-8")
    with pytest.raises(PermissionError):
        read_report(path)


def test_gate_requires_official_current_repo_mapped_user_and_permission(tmp_path, monkeypatch):
    target = tmp_path / "Team.projectos.json"
    create_project("Team", target, state_path=tmp_path / "active.json")
    monkeypatch.setattr("tools.projectos_governance._repository_write_gate", lambda: None)
    monkeypatch.setattr("tools.projectos_governance.authenticated_github_user", lambda: "Kurzschuss")
    monkeypatch.setattr("tools.projectos_governance.load_authorized_developers", lambda: {"kurzschuss"})
    bootstrap_admin(target, display_name="Admin")

    repo = VersionResult(
        status="original_aktuell",
        current=True,
        message="aktuell",
        local_commit="a",
        remote_commit="a",
        branch="main",
        remote_url="https://github.com/Kurzschuss/kicad-din-electrical.git",
        official_remote=True,
        clean_worktree=True,
        authenticated_user="Kurzschuss",
        developer_authorized=True,
    )
    gate = evaluate_auto_report_gate(target, repository=repo)
    assert gate.allowed is True
    assert gate.project_user is not None
    assert gate.project_user.display_name == "Admin"
    assert gate.permission_decision == "allow"

    fork = replace(repo, current=False, official_remote=False, status="nicht_offizielles_repository")
    blocked = evaluate_auto_report_gate(target, repository=fork)
    assert blocked.allowed is False
    assert any("Fork" in reason or "offizielles Repository" in reason for reason in blocked.reasons)


def test_duplicate_summary_reports_original_and_repeat_reporters():
    fingerprint = "a" * 64
    issue_body = f"Text\n<!-- z-report fingerprint={fingerprint} reporter=Uwe -->"
    comments = {
        "comments": [
            {"body": f"<!-- z-duplicate-report fingerprint={fingerprint} reporter=Anna -->"},
            {"body": f"<!-- z-duplicate-report fingerprint={fingerprint} reporter=Uwe -->"},
        ]
    }

    def runner(args):
        if args[:3] == ["gh", "issue", "list"]:
            return cp(args, out=json.dumps([{
                "number": 42,
                "title": "Fehler",
                "state": "OPEN",
                "author": {"login": "Uwe"},
                "createdAt": "2026-08-10T00:00:00Z",
                "url": "https://github.com/Kurzschuss/kicad-din-electrical/issues/42",
                "body": issue_body,
            }]))
        if args[:3] == ["gh", "issue", "view"]:
            return cp(args, out=json.dumps(comments))
        raise AssertionError(args)

    result = duplicate_summary(fingerprint, runner=runner)
    assert result.found is True
    assert result.issue_number == 42
    assert result.report_count == 3
    assert result.reporters == ("Uwe", "Anna")
    assert result.match_type == "fingerprint"


def test_duplicate_summary_recognizes_manual_issue_by_exact_title_and_reference():
    fingerprint = "b" * 64
    title = "Diagnose zeigt falschen Zustand"
    calls = []

    def runner(args):
        calls.append(args)
        if args[:3] == ["gh", "issue", "list"]:
            query = args[args.index("--search") + 1]
            if query.startswith("z-report fingerprint="):
                return cp(args, out="[]")
            assert "in:title" in query
            return cp(args, out=json.dumps([{
                "number": 55,
                "title": title,
                "state": "OPEN",
                "author": {"login": "ManualReporter"},
                "createdAt": "2026-08-09T00:00:00Z",
                "url": "https://github.com/Kurzschuss/kicad-din-electrical/issues/55",
                "body": "Bereits manuell gemeldet. Technische Referenz: PRJ-010",
            }]))
        if args[:3] == ["gh", "issue", "view"]:
            return cp(args, out=json.dumps({"comments": []}))
        raise AssertionError(args)

    result = duplicate_summary(
        fingerprint,
        title=title,
        reference="PRJ-010",
        runner=runner,
    )
    assert result.found is True
    assert result.issue_number == 55
    assert result.original_reporter == "ManualReporter"
    assert result.report_count == 1
    assert result.match_type == "manual_title_reference"
    assert len([call for call in calls if call[:3] == ["gh", "issue", "list"]]) == 2


def test_auto_submit_uses_existing_issue_instead_of_creating_duplicate(tmp_path, monkeypatch):
    report_path = tmp_path / "report.md"
    report_path.write_text(REPORT, encoding="utf-8")
    fingerprint = report_fingerprint(REPORT)
    gate = AutoReportGate(
        allowed=True,
        reasons=(),
        repository_status="original_aktuell",
        repository_message="aktuell",
        official_remote=True,
        current=True,
        clean_worktree=True,
        behind=0,
        branch="main",
        authenticated_github_user="Uwe",
        project_user=ReportIdentity(
            user_id="10000000-0000-0000-0000-000000000001",
            display_name="Uwe",
            github_login="Uwe",
            weight=100,
        ),
        permission_decision="allow",
    )
    monkeypatch.setattr("tools.projectos_issue_reporting.evaluate_auto_report_gate", lambda path: gate)
    calls = []

    def runner(args):
        calls.append(args)
        if args[:3] == ["gh", "issue", "list"]:
            return cp(args, out=json.dumps([{
                "number": 7,
                "title": "Bekannt",
                "state": "OPEN",
                "author": {"login": "Anna"},
                "createdAt": "2026-08-10T00:00:00Z",
                "url": "https://github.com/Kurzschuss/kicad-din-electrical/issues/7",
                "body": f"<!-- z-report fingerprint={fingerprint} reporter=Anna -->",
            }]))
        if args[:3] == ["gh", "issue", "view"]:
            return cp(args, out=json.dumps({"comments": []}))
        if args[:3] == ["gh", "issue", "comment"]:
            return cp(args, out="ok")
        if args[:3] == ["gh", "issue", "create"]:
            raise AssertionError("duplicate must not create a second issue")
        raise AssertionError(args)

    result = submit_auto_report(
        tmp_path / "ignored.projectos.json",
        report_path,
        runner=runner,
        result_path=tmp_path / "result.json",
    )
    assert result.duplicate is True
    assert result.issue_number == 7
    assert result.report_count == 2
    assert result.reporters == ("Anna", "Uwe")
    assert any(call[:3] == ["gh", "issue", "comment"] for call in calls)
