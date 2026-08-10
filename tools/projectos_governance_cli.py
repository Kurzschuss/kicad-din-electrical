"""CLI für vertrauenswürdige ProjectOS-Benutzer- und Rechteänderungen."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.projectos_project_cli import read_active_project
from tools.projectos_governance import (
    add_access_rule,
    bootstrap_admin,
    create_user,
    governance_summary,
    revoke_access_rule,
    update_user,
)


def _active_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    active = read_active_project()
    if active is None:
        raise ValueError("Kein aktives ProjectOS-Projekt vorhanden")
    return active.path


def _print(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _bootstrap(args: argparse.Namespace) -> int:
    return _print(bootstrap_admin(_active_path(args.project), display_name=args.name, weight=args.weight))


def _user_create(args: argparse.Namespace) -> int:
    return _print(create_user(
        _active_path(args.project), display_name=args.name, weight=args.weight,
        github_login=args.github or None,
    ))


def _user_update(args: argparse.Namespace) -> int:
    return _print(update_user(
        _active_path(args.project), user_id=args.user_id, display_name=args.name,
        weight=args.weight, github_login=args.github or None,
    ))


def _rule_add(args: argparse.Namespace) -> int:
    return _print(add_access_rule(
        _active_path(args.project), user_id=args.user_id, permission=args.permission,
        scope=args.scope, list_type=args.list_type, risk_class=args.risk,
    ))


def _rule_revoke(args: argparse.Namespace) -> int:
    return _print(revoke_access_rule(
        _active_path(args.project), assignment_id=args.assignment_id, reason=args.reason,
    ))


def _status(args: argparse.Namespace) -> int:
    return _print(governance_summary(_active_path(args.project)))


def _project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", help="ProjectOS-Projektdatei; ohne Angabe wird das aktive Projekt verwendet")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap", help="ersten Administrator in einem leeren Projekt einrichten")
    _project_argument(bootstrap)
    bootstrap.add_argument("--name", required=True)
    bootstrap.add_argument("--weight", type=int, default=1000)
    bootstrap.set_defaults(handler=_bootstrap)

    user_create = sub.add_parser("user-create", help="Benutzer anlegen")
    _project_argument(user_create)
    user_create.add_argument("--name", required=True)
    user_create.add_argument("--weight", type=int, default=100)
    user_create.add_argument("--github", default="")
    user_create.set_defaults(handler=_user_create)

    user_update = sub.add_parser("user-update", help="Bezeichnung, Gewichtung und GitHub-Zuordnung ändern")
    _project_argument(user_update)
    user_update.add_argument("--user-id", required=True)
    user_update.add_argument("--name", required=True)
    user_update.add_argument("--weight", type=int, required=True)
    user_update.add_argument("--github", default="")
    user_update.set_defaults(handler=_user_update)

    rule_add = sub.add_parser("rule-add", help="Whitelist- oder Blacklist-Regel hinzufügen")
    _project_argument(rule_add)
    rule_add.add_argument("--user-id", required=True)
    rule_add.add_argument("--permission", required=True)
    rule_add.add_argument("--scope", required=True)
    rule_add.add_argument("--list-type", choices=("whitelist", "blacklist"), required=True)
    rule_add.add_argument("--risk", choices=("low", "medium", "high", "critical"), default="medium")
    rule_add.set_defaults(handler=_rule_add)

    rule_revoke = sub.add_parser("rule-revoke", help="bestehende Rechtezuweisung widerrufen")
    _project_argument(rule_revoke)
    rule_revoke.add_argument("--assignment-id", required=True)
    rule_revoke.add_argument("--reason", required=True)
    rule_revoke.set_defaults(handler=_rule_revoke)

    status = sub.add_parser("status", help="Benutzer- und Rechtebestand als JSON ausgeben")
    _project_argument(status)
    status.set_defaults(handler=_status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.handler(args))
    except (OSError, ValueError, PermissionError) as exc:
        raise SystemExit(f"FEHLER: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
