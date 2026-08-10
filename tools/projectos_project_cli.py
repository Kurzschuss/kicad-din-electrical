"""Lokaler Projektdatei-Workflow für das Z_Cockpit.

Die Projektdatei selbst wird ausschließlich über den bestehenden
``DinEditorProjectManager`` erzeugt. Der lokale Aktivzustand unter ``build/``
dient nur dazu, beim nächsten Cockpit-Start dasselbe Projekt wieder zu laden.
Die Schutzklasse ist lokale Workflow-Metadaten; Dateisichtbarkeit muss durch
den tatsächlichen Speicherort bzw. dessen Zugriffskontrolle erzwungen werden.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from distributions.din_editor_project_bundle import DinProjectBundleError
from distributions.din_editor_project_manager import DinEditorProjectManager
from distributions.projectos_project_bundle_v4 import (
    CURRENT_PROJECTOS_BUNDLE_VERSION,
    load_projectos_bundle_details,
)
from tools.z_cockpit.project_access import (
    PROTECTION_LEGACY_UNSPECIFIED,
    PROTECTION_PRIVATE_TEAM,
    normalize_protection_mode,
    validate_project_target,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVE_PROJECT_PATH = ROOT / "build" / "Z_COCKPIT_ACTIVE_PROJECT.json"


@dataclass(frozen=True)
class ActiveProject:
    name: str
    path: Path
    project_id: str
    bundle_version: int = CURRENT_PROJECTOS_BUNDLE_VERSION
    protection_mode: str = PROTECTION_PRIVATE_TEAM

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 2,
            "name": self.name,
            "path": str(self.path),
            "project_id": self.project_id,
            "bundle_version": self.bundle_version,
            "protection_mode": self.protection_mode,
        }


def normalize_project_name(value: str) -> str:
    name = str(value).strip()
    if not name:
        raise ValueError("Projektname darf nicht leer sein")
    if len(name) > 80:
        raise ValueError("Projektname darf höchstens 80 Zeichen enthalten")
    if any(ord(char) < 32 for char in name):
        raise ValueError("Projektname enthält unzulässige Steuerzeichen")
    if any(char in name for char in ("/", "\\", ":", "*", "?", '"', "<", ">", "|")):
        raise ValueError("Projektname enthält unzulässige Dateinamenzeichen")
    return name


def suggested_filename(name: str) -> str:
    normalized = normalize_project_name(name)
    safe = "".join(char if (char.isalnum() or char in " ._()-") else "_" for char in normalized)
    safe = safe.rstrip(" .") or "ProjectOS-Projekt"
    return f"{safe}.projectos.json"


def _write_active_project(item: ActiveProject, state_path: str | Path) -> None:
    target = Path(state_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(item.as_dict(), ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
    temporary.replace(target)


def create_project(
    name: str,
    output: str | Path,
    *,
    state_path: str | Path = DEFAULT_ACTIVE_PROJECT_PATH,
    overwrite: bool = False,
    protection_mode: str = PROTECTION_PRIVATE_TEAM,
    repository_root: str | Path = ROOT,
) -> ActiveProject:
    """Erzeugt ein leeres ProjectOS-v4-Bundle und markiert es lokal als aktiv."""
    normalized_name = normalize_project_name(name)
    normalized_protection = normalize_protection_mode(protection_mode)
    target = Path(output).expanduser().resolve()
    if not target.parent.is_dir():
        raise ValueError(f"Zielordner existiert nicht: {target.parent}")
    validate_project_target(
        target,
        protection_mode=normalized_protection,
        repository_root=repository_root,
    )
    if target.exists() and not overwrite:
        raise FileExistsError(f"Projektdatei existiert bereits: {target}")

    manager = DinEditorProjectManager()
    manager.save(target)
    item = ActiveProject(
        name=normalized_name,
        path=target,
        project_id=manager.project_id,
        protection_mode=normalized_protection,
    )
    _write_active_project(item, state_path)
    return item


def read_active_project(
    state_path: str | Path = DEFAULT_ACTIVE_PROJECT_PATH,
) -> ActiveProject | None:
    """Liest den lokalen Aktivzustand und akzeptiert nur ein noch gültiges v4-Bundle."""
    source = Path(state_path)
    if not source.is_file():
        return None
    try:
        raw: Any = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return None
        schema_version = int(raw.get("schema_version", 0))
        if schema_version not in {1, 2}:
            return None
        name = normalize_project_name(str(raw["name"]))
        path = Path(str(raw["path"])).expanduser().resolve()
        expected_project_id = str(raw["project_id"])
        expected_version = int(raw.get("bundle_version", 0))
        if schema_version == 1:
            protection_mode = PROTECTION_LEGACY_UNSPECIFIED
        else:
            protection_mode = normalize_protection_mode(str(raw["protection_mode"]))
        if expected_version != CURRENT_PROJECTOS_BUNDLE_VERSION or not path.is_file():
            return None
        _, _, project_id, migration_required, _ = load_projectos_bundle_details(path)
        if migration_required or project_id != expected_project_id:
            return None
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, DinProjectBundleError):
        return None
    return ActiveProject(
        name=name,
        path=path,
        project_id=expected_project_id,
        protection_mode=protection_mode,
    )


def _command_new(args: argparse.Namespace) -> int:
    item = create_project(
        args.name,
        args.output,
        state_path=args.state_path,
        overwrite=args.overwrite,
        protection_mode=args.protection,
    )
    print(json.dumps(item.as_dict(), ensure_ascii=False))
    return 0


def _command_active(args: argparse.Namespace) -> int:
    item = read_active_project(args.state_path)
    if item is None:
        return 0
    if args.path_only:
        print(item.path)
    else:
        print(json.dumps(item.as_dict(), ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="neues ProjectOS-v4-Projekt erzeugen")
    new.add_argument("--name", required=True, help="Projektname")
    new.add_argument("--output", required=True, help="Zieldatei")
    new.add_argument(
        "--protection",
        default=PROTECTION_PRIVATE_TEAM,
        help="Schutzklasse: private_team, restricted_local oder repository_visible",
    )
    new.add_argument("--state-path", default=str(DEFAULT_ACTIVE_PROJECT_PATH), help=argparse.SUPPRESS)
    new.add_argument("--overwrite", action="store_true", help="nach bestätigtem Speichern-unter-Dialog überschreiben")
    new.set_defaults(handler=_command_new)

    active = sub.add_parser("active", help="lokal aktives Projekt ermitteln")
    active.add_argument("--state-path", default=str(DEFAULT_ACTIVE_PROJECT_PATH), help=argparse.SUPPRESS)
    active.add_argument("--path-only", action="store_true", help="nur den Projektpfad ausgeben")
    active.set_defaults(handler=_command_active)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.handler(args))
    except (OSError, ValueError, DinProjectBundleError) as exc:
        raise SystemExit(f"FEHLER: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
