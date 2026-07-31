"""Combined DIN editor project state including synchronization audit history."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


class DinProjectBundleError(ValueError):
    """Raised when a DIN editor project file cannot be loaded or saved safely."""


def _save_json_atomic(payload: object, path: str | Path) -> Path:
    target = Path(path)
    temporary: Path | None = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(target)
    except (OSError, TypeError, ValueError) as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise DinProjectBundleError(f"DIN project file cannot be saved: {target}") from exc
    return target


def _load_json(path: str | Path) -> object:
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DinProjectBundleError(f"DIN project file not found: {source}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise DinProjectBundleError(f"DIN project file cannot be read: {source}") from exc
    except json.JSONDecodeError as exc:
        raise DinProjectBundleError(f"DIN project file contains invalid JSON: {source}") from exc


def export_project_bundle(session: DinEditorSession, sync_log: DinSyncLog | None = None) -> dict:
    return {
        "version": 2,
        "session": export_session(session),
        "sync_log": (sync_log or DinSyncLog()).export(),
    }


def import_project_bundle(data: dict) -> tuple[DinEditorSession, DinSyncLog]:
    if not isinstance(data, dict):
        raise DinProjectBundleError("invalid DIN editor project bundle")
    try:
        version = int(data.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise DinProjectBundleError("invalid DIN editor project bundle version") from exc
    if version != 2:
        raise DinProjectBundleError("unsupported DIN editor project bundle version")
    try:
        session = import_session(data.get("session", {}))
        entries = data.get("sync_log", [])
        if not isinstance(entries, list):
            raise ValueError("synchronization log must be a list")
        log = DinSyncLog()
        log.entries = [dict(entry) for entry in entries]
        return session, log
    except (TypeError, ValueError, KeyError) as exc:
        raise DinProjectBundleError("invalid DIN editor project data") from exc


def save_project_bundle(session: DinEditorSession, sync_log: DinSyncLog | None, path: str | Path) -> Path:
    return _save_json_atomic(export_project_bundle(session, sync_log), path)


def load_project_bundle(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    data = _load_json(path)
    return import_project_bundle(data)
