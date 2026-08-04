from __future__ import annotations

import argparse
import datetime as dt
import platform
import subprocess
from pathlib import Path


def _run_git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "nicht verfügbar"


def build_report(title: str, command: str, exit_code: int, log_text: str) -> str:
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    branch = _run_git("branch", "--show-current")
    commit = _run_git("rev-parse", "HEAD")
    status = _run_git("status", "--short") or "Arbeitsverzeichnis sauber"
    safe_log = log_text.rstrip() or "Keine zusätzliche Konsolenausgabe erfasst."
    return f"""# Automatischer Fehlerbericht

## Zusammenfassung

- **Prüfung:** {title}
- **Zeitpunkt:** {now}
- Fehlercode: `{exit_code}`
- **Befehl:** `{command}`

## Umgebung

- **Betriebssystem:** {platform.platform()}
- **Python:** {platform.python_version()}
- **Arbeitsordner:** `{Path.cwd()}`
- **Git-Branch:** `{branch}`
- **Git-Commit:** `{commit}`

## Git-Status

```text
{status}
```

## Vollständige Fehlermeldung

```text
{safe_log}
```

## Schritte zum Nachstellen

1. Repository im oben genannten Commit auschecken.
2. Entwicklungsumgebung mit `run_tests.bat` einrichten.
3. Den dokumentierten Befehl erneut ausführen.

## Erwartetes Ergebnis

Die Prüfung wird ohne Fehlercode beendet.

## Tatsächliches Ergebnis

Die Prüfung wurde mit Fehlercode `{exit_code}` beendet.

---

Dieser Bericht wurde automatisch erzeugt und kann unverändert als GitHub-Issue-Text verwendet werden.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Erzeugt einen GitHub-tauglichen Markdown-Fehlerbericht.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--exit-code", required=True, type=int)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--output", type=Path, default=Path("build/FEHLERBERICHT.md"))
    args = parser.parse_args()

    log_text = ""
    if args.log and args.log.exists():
        log_text = args.log.read_text(encoding="utf-8", errors="replace")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        build_report(args.title, args.command, args.exit_code, log_text),
        encoding="utf-8",
    )
    print(f"Fehlerbericht erzeugt: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
