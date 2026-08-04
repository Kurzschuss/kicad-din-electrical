from __future__ import annotations

import argparse
import re
from pathlib import Path


WINDOWS_USER_PATH = re.compile(r"(?i)([A-Z]:\\Users\\)[^\\\r\n]+")
SECRET_ASSIGNMENT = re.compile(
    r"(?im)\b(token|api[_-]?key|secret|password|passwd)\b\s*[:=]\s*([^\s`]+)"
)
SUMMARY_TITLE = re.compile(r"^- \*\*Prüfung:\*\*\s*(.+)$", re.MULTILINE)


def redact_sensitive_text(text: str) -> str:
    """Maskiert lokale Benutzerpfade und typische Zugangsdaten."""
    text = WINDOWS_USER_PATH.sub(r"\1<Benutzer>", text)
    return SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=<MASKIERT>", text)


def extract_issue_title(report_text: str) -> str:
    match = SUMMARY_TITLE.search(report_text)
    title = match.group(1).strip() if match else "Automatischer Fehlerbericht"
    return f"[Fehlerbericht] {title}"[:256]


def build_issue_preview(report_text: str) -> tuple[str, str]:
    cleaned = redact_sensitive_text(report_text).rstrip()
    title = extract_issue_title(cleaned)
    body = f"""<!-- Lokale Vorschau. Vor Veröffentlichung vollständig prüfen. -->

{cleaned}

---

> Diese GitHub-Issue-Vorschau wurde lokal erzeugt. Es wurde nichts veröffentlicht.
"""
    return title, body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Erzeugt aus einem Fehlerbericht eine lokale GitHub-Issue-Vorschau."
    )
    parser.add_argument("--report", type=Path, default=Path("build/FEHLERBERICHT.md"))
    parser.add_argument(
        "--output", type=Path, default=Path("build/GITHUB_ISSUE_VORSCHAU.md")
    )
    parser.add_argument(
        "--title-output", type=Path, default=Path("build/GITHUB_ISSUE_TITEL.txt")
    )
    args = parser.parse_args()

    if not args.report.exists():
        parser.error(f"Fehlerbericht nicht gefunden: {args.report}")

    report_text = args.report.read_text(encoding="utf-8", errors="replace")
    title, body = build_issue_preview(report_text)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(body, encoding="utf-8")
    args.title_output.write_text(title + "\n", encoding="utf-8")

    print(f"Issue-Titel: {title}")
    print(f"Issue-Vorschau erzeugt: {args.output}")
    print(f"Titeldatei erzeugt: {args.title_output}")
    print("Es wurde nichts auf GitHub veröffentlicht.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
