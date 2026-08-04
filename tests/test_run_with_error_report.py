from __future__ import annotations

import sys
from pathlib import Path

from tools.run_with_error_report import run_command


def test_success_writes_log_without_report(tmp_path: Path) -> None:
    log_path = tmp_path / "lauf.log"
    report_path = tmp_path / "bericht.md"

    result = run_command(
        "Erfolgreicher Test",
        [sys.executable, "-c", "print('alles gut')"],
        log_path,
        report_path,
    )

    assert result == 0
    assert "alles gut" in log_path.read_text(encoding="utf-8")
    assert not report_path.exists()


def test_failure_writes_log_and_report(tmp_path: Path) -> None:
    log_path = tmp_path / "lauf.log"
    report_path = tmp_path / "bericht.md"

    result = run_command(
        "Fehlgeschlagener Test",
        [sys.executable, "-c", "import sys; print('kaputt'); sys.exit(3)"],
        log_path,
        report_path,
    )

    assert result == 3
    assert "kaputt" in log_path.read_text(encoding="utf-8")
    report = report_path.read_text(encoding="utf-8")
    assert "Fehlgeschlagener Test" in report
    assert "Fehlercode: `3`" in report
    assert "kaputt" in report
