from pathlib import Path


def test_all_checks_use_automatic_error_reports() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    expected_calls = (
        '"Repository-Health-Check" "build\\ALLE_PRUEFUNGEN_HEALTH.log" python -m pytest -q %HEALTH_TEST%',
        '"Vollstaendige Testsuite" "build\\ALLE_PRUEFUNGEN_PYTEST.log" python -m pytest -q',
        '"Python-Syntaxpruefung" "build\\ALLE_PRUEFUNGEN_SYNTAX.log" python -m compileall -q distributions tests tools',
        '"Z_-Qualitaetspruefung" "build\\ALLE_PRUEFUNGEN_QUALITAET.log" %QUALITY_CMD%',
    )

    allchecks = content.split("\n:allchecks\n", 1)[1].split("\n:allchecks_failed\n", 1)[0]

    for expected_call in expected_calls:
        assert expected_call in allchecks

    assert allchecks.count('tools\\windows\\run_with_error_report.bat') == 4
    assert "build\\FEHLERBERICHT.md" not in allchecks

    failure_block = content.split("\n:allchecks_failed\n", 1)[1].split(
        "\n:run_pytest\n", 1
    )[0]
    assert "build\\FEHLERBERICHT.md" in failure_block
