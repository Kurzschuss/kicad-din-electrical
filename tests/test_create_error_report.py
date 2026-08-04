from __future__ import annotations

from tools.create_error_report import build_report


def test_build_report_contains_github_ready_sections() -> None:
    report = build_report(
        title="Python-Syntaxprüfung",
        command="python -m compileall -q distributions tests tools",
        exit_code=1,
        log_text="SyntaxError: unexpected character after line continuation character",
    )

    assert report.startswith("# Automatischer Fehlerbericht")
    assert "## Zusammenfassung" in report
    assert "## Umgebung" in report
    assert "## Vollständige Fehlermeldung" in report
    assert "## Schritte zum Nachstellen" in report
    assert "Python-Syntaxprüfung" in report
    assert "SyntaxError" in report
    assert "Fehlercode: `1`" in report
    assert "GitHub-Issue-Text" in report


def test_build_report_documents_missing_console_output() -> None:
    report = build_report("Test", "python -m pytest", 2, "")
    assert "Keine zusätzliche Konsolenausgabe erfasst." in report
