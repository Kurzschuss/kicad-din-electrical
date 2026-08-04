from pathlib import Path


def test_all_checks_use_automatic_error_reports() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    expected_calls = (
        '"Vollstaendige Testsuite" "build\\ALLE_PRUEFUNGEN_PYTEST.log" python -m pytest -q',
        '"Python-Syntaxpruefung" "build\\ALLE_PRUEFUNGEN_SYNTAX.log" python -m compileall -q distributions tests tools',
        '"Z_-Qualitaetspruefung" "build\\ALLE_PRUEFUNGEN_QUALITAET.log" %QUALITY_CMD%',
    )

    for expected_call in expected_calls:
        assert expected_call in content

    allchecks = content.split(":allchecks", 1)[1].split(":help", 1)[0]
    assert allchecks.count('tools\\windows\\run_with_error_report.bat') == 3
    assert "build\\FEHLERBERICHT.md" in allchecks
