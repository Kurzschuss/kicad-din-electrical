"""Combined DIN editor project state including synchronization audit history."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session


class DinProjectBundleError(ValueError):
    """Raised when a DIN editor project file cannot be loaded or saved safely."""


def recovery_path_for(path: str | Path) -> Path:
    target = Path(path)
    return target.with_name(f".{target.name}.recovery")


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


def _save_bytes_atomic(payload: bytes, path: str | Path) -> Path:
    target = Path(path)
    temporary: Path | None = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("wb", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(target)
    except OSError as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise DinProjectBundleError(f"DIN recovery file cannot be saved: {target}") from exc
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
    return {"version": 2, "session": export_session(session), "sync_log": (sync_log or DinSyncLog()).export()}


def _validate_sync_entry(entry: object) -> dict:
    if not isinstance(entry, dict):
        raise ValueError("synchronization log entry must be an object")
    required = ("timestamp", "reference", "source", "value", "action")
    if any(key not in entry for key in required):
        raise ValueError("synchronization log entry is incomplete")
    if any(not isinstance(entry[key], str) for key in required):
        raise ValueError("synchronization log entry fields must be strings")
    try:
        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("synchronization log timestamp must be ISO-8601") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("synchronization log timestamp must include a timezone")
    timestamp = timestamp.astimezone(timezone.utc)
    if timestamp > datetime.now(timezone.utc):
        raise ValueError("synchronization log timestamp cannot be in the future")
    clean = {key: entry[key] for key in required}
    clean["timestamp"] = timestamp.isoformat()
    if not clean["reference"].strip():
        raise ValueError("synchronization log reference is required")
    if not clean["source"].strip():
        raise ValueError("synchronization log source is required")
    if not clean["action"].strip():
        raise ValueError("synchronization log action is required")
    return clean


def import_project_bundle(data: dict) -> tuple[DinEditorSession, DinSyncLog]:
    if not isinstance(data, dict):
        raise DinProjectBundleError("invalid DIN editor project bundle")
    try:
        version = int(data.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise DinProjectBundleError("invalid DIN editor project bundle version") from exc
    if version != 2:
        raise DinProjectBundleError("unsupported DIN editor project bundle version")
    session_data = data.get("session")
    entries = data.get("sync_log")
    if not isinstance(session_data, dict):
        raise DinProjectBundleError("invalid DIN editor project session")
    if not isinstance(entries, list):
        raise DinProjectBundleError("invalid DIN synchronization log")
    try:
        session = import_session(session_data)
        validated_entries = [_validate_sync_entry(entry) for entry in entries]
    except (TypeError, ValueError, KeyError) as exc:
        raise DinProjectBundleError("invalid DIN editor project data") from exc
    log = DinSyncLog()
    log.entries = validated_entries
    return session, log


def load_project_bundle(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    data = _load_json(path)
    return import_project_bundle(data)


def recovery_status_for(path: str | Path) -> dict:
    recovery = recovery_path_for(path)
    status = {
        "path": str(recovery),
        "available": recovery.exists(),
        "valid": None,
        "can_recover": False,
        "error": None,
    }
    if not status["available"]:
        return status
    try:
        session, _ = load_project_bundle(recovery)
    except DinProjectBundleError as exc:
        status["valid"] = False
        status["error"] = str(exc)
        return status
    issues = validate_session(session)
    if issues:
        status["valid"] = False
        status["error"] = "; ".join(issue.message for issue in issues)
        return status
    status["valid"] = True
    status["can_recover"] = True
    return status


def _preserve_last_valid_project(path: str | Path) -> Path | None:
    target = Path(path)
    if not target.exists():
        return None
    try:
        session, _ = load_project_bundle(target)
    except DinProjectBundleError:
        return None
    if validate_session(session):
        return None
    recovery = recovery_path_for(target)
    return _save_bytes_atomic(target.read_bytes(), recovery)


def save_project_bundle(session: DinEditorSession, sync_log: DinSyncLog | None, path: str | Path) -> Path:
    target = Path(path)
    _preserve_last_valid_project(target)
    return _save_json_atomic(export_project_bundle(session, sync_log), target)


def load_project_recovery(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    recovery = recovery_path_for(path)
    try:
        session, sync_log = load_project_bundle(recovery)
    except DinProjectBundleError as exc:
        raise DinProjectBundleError(f"DIN project recovery cannot be loaded: {recovery}") from exc
    issues = validate_session(session)
    if issues:
        raise DinProjectBundleError(
            f"DIN project recovery validation failed: {recovery}: "
            + "; ".join(issue.message for issue in issues)
        )
    return session, sync_log