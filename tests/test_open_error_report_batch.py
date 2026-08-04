from pathlib import Path


def test_open_error_report_batch_has_controlled_actions() -> None:
    text = Path("tools/windows/open_error_report.bat").read_text(encoding="utf-8")

    assert "build\\FEHLERBERICHT.md" in text
    assert "build\\GITHUB_ISSUE_VORSCHAU.md" in text
    assert "build\\GITHUB_ISSUE_TITEL.txt" in text
    assert "[1] Fehlerbericht oeffnen" in text
    assert "[2] Fehlerordner im Explorer oeffnen" in text
    assert "[3] GitHub-Issue-Vorschau erzeugen und oeffnen" in text
    assert "[0] Zurueck" in text
    assert 'start "" "%REPORT_FILE%"' in text
    assert 'start "" "%ISSUE_PREVIEW%"' in text
    assert "explorer.exe /select" in text
    assert "python -m tools.create_github_issue_preview" in text
    assert "Es wurde nichts auf GitHub veroeffentlicht." in text
    assert "gh issue create" not in text
    assert "create_issue" not in text
