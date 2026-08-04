from pathlib import Path


def test_single_checks_use_error_report_adapter() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    assert 'tools\\windows\\run_with_error_report.bat' in content
    assert 'build\\LETZTER_TESTLAUF.log' in content
    assert 'build\\FEHLERBERICHT.md' in content
    assert ':run' in content


def test_help_mentions_automatic_error_reports() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    assert "AUTOMATISCHE FEHLERBERICHTE" in content
    assert "GitHub-Issue" in content
