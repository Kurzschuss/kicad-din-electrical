from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from tools.create_error_report import build_report


def run_command(title: str, command: list[str], log_path: Path, report_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    collected: list[str] = []
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        text = f"Befehl konnte nicht gestartet werden: {exc}\n"
        print(text, end="", file=sys.stderr)
        log_path.write_text(text, encoding="utf-8")
        report_path.write_text(build_report(title, subprocess.list2cmdline(command), 127, text), encoding="utf-8")
        return 127

    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        collected.append(line)

    exit_code = process.wait()
    log_text = "".join(collected)
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
