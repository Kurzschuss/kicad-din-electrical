from pathlib import Path


def test_open_error_report_batch_has_controlled_actions() -> None:
    text = Path("tools/windows/open_error_report.bat").read_text(encoding="utf-8")

    assert "build\\FEHLERBERICHT.md" in text
    assert "[1] Fehlerbericht oeffnen" in text
    assert "[2] Fehlerordner im Explorer oeffnen" in text
    assert "[0] Zurueck" in text
    assert 'start "" "%REPORT_FILE%"' in text
    assert "explorer.exe /select" in text
    assert "GitHub" not in text
