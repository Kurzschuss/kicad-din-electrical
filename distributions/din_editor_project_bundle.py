"""Combined DIN editor project state including synchronization audit history."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID, uuid4
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session


CURRENT_BUNDLE_VERSION = 3
LEGACY_BUNDLE_VERSION = 2


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


def _normalize_project_id(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DinProjectBundleError("invalid DIN editor project id")
    try:
        return str(UUID(value))
    except (ValueError, AttributeError) as exc:
        raise DinProjectBundleError("invalid DIN editor project id") from exc


def export_project_bundle(
    session: DinEditorSession,
    sync_log: DinSyncLog | None = None,
    *,
    project_id: str | None = None,
) -> dict:
    stable_project_id = _normalize_project_id(project_id) if project_id is not None else str(uuid4())
    return {
        "version": CURRENT_BUNDLE_VERSION,
        "project_id": stable_project_id,
        "session": export_session(session),
        "sync_log": (sync_log or DinSyncLog()).export(),
    }


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
    for field_name in ("project_id", "command_id", "correlation_id", "causation_id"):
        if field_name in entry:
            clean[field_name] = str(UUID(str(entry[field_name])))
    return clean


def import_project_bundle_details(data: dict) -> tuple[DinEditorSession, DinSyncLog, str | None, bool]:
    if not isinstance(data, dict):
        raise DinProjectBundleError("invalid DIN editor project bundle")
    try:
        version = int(data.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise DinProjectBundleError("invalid DIN editor project bundle version") from exc
    if version not in (LEGACY_BUNDLE_VERSION, CURRENT_BUNDLE_VERSION):
        raise DinProjectBundleError("unsupported DIN editor project bundle version")

    project_id: str | None = None
    migration_required = version == LEGACY_BUNDLE_VERSION
    if version == CURRENT_BUNDLE_VERSION:
        project_id = _normalize_project_id(data.get("project_id"))

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
    return session, log, project_id, migration_required


def import_project_bundle(data: dict) -> tuple[DinEditorSession, DinSyncLog]:
    session, log, _, _ = import_project_bundle_details(data)
    return session, log


def load_project_bundle_details(path: str | Path) -> tuple[DinEditorSession, DinSyncLog, str | None, bool]:
    data = _load_json(path)
    return import_project_bundle_details(data)


def load_project_bundle(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    session, log, _, _ = load_project_bundle_details(path)
    return session, log


def _recovery_metadata(target: Path, recovery: Path) -> dict:
    metadata = {
        "source_path": str(target),
        "recovery_path": str(recovery),
        "captured_at": None,
        "bundle_version": None,
        "session_version": None,
        "project_id": None,
    }
    if not recovery.exists():
        return metadata
    try:
        metadata["captured_at"] = datetime.fromtimestamp(
            recovery.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
    except OSError:
        pass
    try:
        raw = _load_json(recovery)
    except DinProjectBundleError:
        return metadata
    if isinstance(raw, dict):
        metadata["bundle_version"] = raw.get("version")
        raw_project_id = raw.get("project_id")
        if raw_project_id is not None:
            try:
                metadata["project_id"] = _normalize_project_id(raw_project_id)
            except DinProjectBundleError:
                metadata["project_id"] = None
        session_data = raw.get("session")
        if isinstance(session_data, dict):
            metadata["session_version"] = session_data.get("version")
    return metadata


def recovery_status_for(path: str | Path) -> dict:
    target = Path(path)
    recovery = recovery_path_for(target)
    status = {
        "path": str(recovery),
        "available": recovery.exists(),
        "valid": None,
        "can_recover": False,
        "error": None,
        "metadata": _recovery_metadata(target, recovery),
    }
    if not status["available"]:
        return status
    try:
        session, _, _, _ = load_project_bundle_details(recovery)
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
        session, _, _, _ = load_project_bundle_details(target)
    except DinProjectBundleError:
        return None
    if validate_session(session):
        return None
    recovery = recovery_path_for(target)
    return _save_bytes_atomic(target.read_bytes(), recovery)


def save_project_bundle(
    session: DinEditorSession,
    sync_log: DinSyncLog | None,
    path: str | Path,
    *,
    project_id: str | None = None,
) -> Path:
    target = Path(path)
    _preserve_last_valid_project(target)
    return _save_json_atomic(export_project_bundle(session, sync_log, project_id=project_id), target)


def load_project_recovery_details(path: str | Path) -> tuple[DinEditorSession, DinSyncLog, str | None, bool]:
    recovery = recovery_path_for(path)
    try:
        session, sync_log, project_id, migration_required = load_project_bundle_details(recovery)
    except DinProjectBundleError as exc:
        raise DinProjectBundleError(f"DIN project recovery cannot be loaded: {recovery}") from exc
    issues = validate_session(session)
    if issues:
        raise DinProjectBundleError(
            f"DIN project recovery validation failed: {recovery}: "
            + "; ".join(issue.message for issue in issues)
        )
    return session, sync_log, project_id, migration_required


def load_project_recovery(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    session, sync_log, _, _ = load_project_recovery_details(path)
    return session, sync_log
