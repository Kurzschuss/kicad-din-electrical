from pathlib import Path


def test_single_checks_use_error_report_adapter() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    assert 'tools\\windows\\run_with_error_report.bat' in content
    assert 'build\\LETZTER_TESTLAUF.log' in content
    assert 'build\\FEHLERBERICHT.md' in content
    assert ':run' in content


def test_error_report_adapter_forwards_only_command_arguments() -> None:
    content = Path("tools/windows/run_with_error_report.bat").read_text(
        encoding="utf-8"
    )

    assert 'set "REPORT_TITLE=%~1"' in content
    assert 'set "REPORT_LOG=%~2"' in content
    assert content.count("shift") >= 3
    assert ':collect_command_args' in content
    assert 'set "COMMAND_ARGS=%COMMAND_ARGS% "%~1""' in content
    assert '-- "%COMMAND_EXE%" %COMMAND_ARGS:* =%' in content
    assert '-- %COMMAND_ARGS%' not in content
    assert '-- %*' not in content


def test_error_report_adapter_uses_project_venv_python() -> None:
    content = Path("tools/windows/run_with_error_report.bat").read_text(
        encoding="utf-8"
    )

    assert 'set "PYTHON_EXE=%~dp0..\\..\\.venv\\Scripts\\python.exe"' in content
    assert 'if /I "%COMMAND_EXE%"=="python" set "COMMAND_EXE=%PYTHON_EXE%"' in content
    assert '"%PYTHON_EXE%" -m tools.run_with_error_report' in content


def test_error_report_adapter_opens_local_action_dialog_after_failure() -> None:
    content = Path("tools/windows/run_with_error_report.bat").read_text(
        encoding="utf-8"
    )

    assert 'if not "%RESULT%"=="0"' in content
    assert 'call "tools\\windows\\open_error_report.bat"' in content
    assert content.index('if not "%RESULT%"=="0"') < content.index(
        'call "tools\\windows\\open_error_report.bat"'
    )


def test_help_mentions_automatic_error_reports() -> None:
    content = Path("run_tests.bat").read_text(encoding="utf-8")

    assert "AUTOMATISCHE FEHLERBERICHTE" in content
    assert "GitHub-Issue" in content
