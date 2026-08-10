"""CLI für ProjectOS-GitHub-Meldegate, Dublettenprüfung und automatisches Senden."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from tools.projectos_issue_reporting import (
    duplicate_summary,
    evaluate_auto_report_gate,
    read_report,
    report_fingerprint,
    submit_auto_report,
)
from tools.projectos_project_cli import read_active_project


def _project_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    active = read_active_project()
    if active is None:
        raise ValueError("Kein aktives ProjectOS-Projekt vorhanden")
    return active.path


def _json(payload) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _gate(args: argparse.Namespace) -> int:
    return _json(asdict(evaluate_auto_report_gate(_project_path(args.project))))


def _duplicate(args: argparse.Namespace) -> int:
    report = read_report(args.report_file)
    fingerprint = report_fingerprint(report)
    payload = asdict(duplicate_summary(fingerprint))
    payload["fingerprint"] = fingerprint
    return _json(payload)


def _auto(args: argparse.Namespace) -> int:
    return _json(asdict(submit_auto_report(
        _project_path(args.project), args.report_file,
        result_path=args.result_path,
    )))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    gate = sub.add_parser("gate", help="Repository-, Benutzer- und Rechtegate prüfen")
    gate.add_argument("--project")
    gate.set_defaults(handler=_gate)

    duplicate = sub.add_parser("duplicate", help="Dublettenstatus für einen Bericht prüfen")
    duplicate.add_argument("--report-file", required=True)
    duplicate.set_defaults(handler=_duplicate)

    auto = sub.add_parser("auto", help="Bericht nach vollständiger Prüfung automatisch senden")
    auto.add_argument("--project")
    auto.add_argument("--report-file", required=True)
    auto.add_argument("--result-path", default="build/Z_ISSUE_REPORTING_RESULT.json")
    auto.set_defaults(handler=_auto)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.handler(args))
    except (OSError, ValueError, PermissionError, RuntimeError) as exc:
        raise SystemExit(f"FEHLER: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
