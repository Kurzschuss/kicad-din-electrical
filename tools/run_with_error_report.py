from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from tools.create_error_report import build_report


def _configure_utf8_console() -> None:
    """Verhindert verstümmelte Umlaute in Windows-Testausgaben."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _utf8_subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    return environment


def _compact_percent_progress(line: str) -> tuple[int, str] | None:
    """Verdichtet FreeCAD-Zeilen wie ``(37 %)`` auf 10-Prozent-Schritte."""
    match = re.fullmatch(r"\s*\((\d{1,3})\s*%\)\s*", line)
    if not match:
        return None

    percent = max(0, min(100, int(match.group(1))))
    if percent not in {0, 100} and percent % 10 != 0:
        return percent, ""

    width = 20
    filled = round(width * percent / 100)
    bar = "#" * filled + "." * (width - filled)
    return percent, f"3D-Export: [{bar}] {percent:3d} %\n"


def run_command(title: str, command: list[str], log_path: Path, report_path: Path) -> int:
    _configure_utf8_console()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    collected: list[str] = []
    emitted_progress: set[int] = set()
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_utf8_subprocess_environment(),
        )
    except OSError as exc:
        text = f"Befehl konnte nicht gestartet werden: {exc}\n"
        print(text, end="", file=sys.stderr)
        log_path.write_text(text, encoding="utf-8")
        report_path.write_text(
            build_report(title, subprocess.list2cmdline(command), 127, text),
            encoding="utf-8",
        )
        return 127

    assert process.stdout is not None
    for line in process.stdout:
        progress = _compact_percent_progress(line)
        if progress is not None:
            percent, compact_line = progress
            if compact_line and percent not in emitted_progress:
                print(compact_line, end="")
                collected.append(compact_line)
                emitted_progress.add(percent)
            continue

        print(line, end="")
        collected.append(line)

    exit_code = process.wait()
    log_text = "".join(collected)
    if exit_code == 0 and not log_text.strip():
        log_text = (
            f"Prüfung: {title}\n"
            "Status: ERFOLGREICH\n"
            f"Befehl: {subprocess.list2cmdline(command)}\n"
            "Ausgabe: keine; der Befehl wurde ohne Fehler beendet.\n"
        )
        print(log_text, end="")
    log_path.write_text(log_text, encoding="utf-8")

    if exit_code != 0:
        report_path.write_text(
            build_report(title, subprocess.list2cmdline(command), exit_code, log_text),
            encoding="utf-8",
        )
        print()
        print(f"Fehlerbericht erzeugt: {report_path}")

    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Führt einen Befehl aus und erzeugt bei Fehlern einen GitHub-tauglichen Bericht."
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--log", type=Path, default=Path("build/LETZTER_TESTLAUF.log"))
    parser.add_argument("--report", type=Path, default=Path("build/FEHLERBERICHT.md"))
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("Nach -- muss ein auszuführender Befehl angegeben werden.")

    return run_command(args.title, command, args.log, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
