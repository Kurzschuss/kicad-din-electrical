"""ProjectOS-Projektbundle v4 mit optionaler Benutzerverwaltung.

Die bestehende DIN-Bundle-v2/v3-Implementierung bleibt unverändert. Diese Schicht
liest v2/v3 kompatibel und erweitert v4 ausschließlich um den fachlichen
`user_management`-Persistenzblock.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .din_editor_project_bundle import (
    DinProjectBundleError,
    _load_json,
    _normalize_project_id,
    _save_bytes_atomic,
    _save_json_atomic,
    import_project_bundle_details as import_legacy_bundle_details,
    recovery_path_for,
)
from .din_editor_serialization import export_session
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session
from .projectos_user_management_persistence import ProjectOSUserManagementState

CURRENT_PROJECTOS_BUNDLE_VERSION = 4
LEGACY_BUNDLE_VERSIONS = {2, 3}


def empty_user_management(project_id: str) -> ProjectOSUserManagementState:
    return ProjectOSUserManagementState(project_id=project_id)


def export_projectos_bundle(
    session: DinEditorSession,
    sync_log: DinSyncLog | None = None,
    *,
    project_id: str,
    user_management: ProjectOSUserManagementState | None = None,
) -> dict[str, Any]:
    stable_project_id = _normalize_project_id(project_id)
    state = user_management or empty_user_management(stable_project_id)
    if state.project_id != stable_project_id:
        raise DinProjectBundleError("user management belongs to another project")
    return {
        "version": CURRENT_PROJECTOS_BUNDLE_VERSION,
        "project_id": stable_project_id,
        "session": export_session(session),
        "sync_log": (sync_log or DinSyncLog()).export(),
        "user_management": state.as_dict(),
    }


def import_projectos_bundle_details(
    data: dict[str, Any],
) -> tuple[DinEditorSession, DinSyncLog, str | None, bool, ProjectOSUserManagementState | None]:
    if not isinstance(data, dict):
        raise DinProjectBundleError("invalid DIN editor project bundle")
    try:
        version = int(data.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise DinProjectBundleError("invalid DIN editor project bundle version") from exc

    if version in LEGACY_BUNDLE_VERSIONS:
        session, log, project_id, legacy_migration = import_legacy_bundle_details(data)
        # v2 besitzt noch keine stabile project_id; sie wird wie bisher erst im Manager erzeugt.
        migration_required = True
        user_management = empty_user_management(project_id) if project_id is not None else None
        return session, log, project_id, migration_required or legacy_migration, user_management

    if version != CURRENT_PROJECTOS_BUNDLE_VERSION:
        raise DinProjectBundleError("unsupported DIN editor project bundle version")

    project_id = _normalize_project_id(data.get("project_id"))
    legacy_payload = {
        "version": 3,
        "project_id": project_id,
        "session": data.get("session"),
        "sync_log": data.get("sync_log"),
    }
    session, log, _, _ = import_legacy_bundle_details(legacy_payload)
    raw_user_management = data.get("user_management")
    if raw_user_management is None:
        user_management = empty_user_management(project_id)
    else:
        try:
            user_management = ProjectOSUserManagementState.from_dict(raw_user_management)
        except (TypeError, ValueError, KeyError) as exc:
            raise DinProjectBundleError("invalid ProjectOS user management data") from exc
        if user_management.project_id != project_id:
            raise DinProjectBundleError("user management belongs to another project")
    return session, log, project_id, False, user_management


def load_projectos_bundle_details(
    path: str | Path,
) -> tuple[DinEditorSession, DinSyncLog, str | None, bool, ProjectOSUserManagementState | None]:
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise DinProjectBundleError("invalid DIN editor project bundle")
    return import_projectos_bundle_details(raw)


def _preserve_last_valid_project(path: str | Path) -> Path | None:
    target = Path(path)
    if not target.exists():
        return None
    try:
        session, _, _, _, _ = load_projectos_bundle_details(target)
    except DinProjectBundleError:
        return None
    if validate_session(session):
        return None
    recovery = recovery_path_for(target)
    return _save_bytes_atomic(target.read_bytes(), recovery)


def save_projectos_bundle(
    session: DinEditorSession,
    sync_log: DinSyncLog | None,
    path: str | Path,
    *,
    project_id: str,
    user_management: ProjectOSUserManagementState | None = None,
) -> Path:
    target = Path(path)
    _preserve_last_valid_project(target)
    payload = export_projectos_bundle(
        session,
        sync_log,
        project_id=project_id,
        user_management=user_management,
    )
    return _save_json_atomic(payload, target)


def load_projectos_recovery_details(
    path: str | Path,
) -> tuple[DinEditorSession, DinSyncLog, str | None, bool, ProjectOSUserManagementState | None]:
    recovery = recovery_path_for(path)
    try:
        session, log, project_id, migration_required, user_management = load_projectos_bundle_details(recovery)
    except DinProjectBundleError as exc:
        raise DinProjectBundleError(f"DIN project recovery cannot be loaded: {recovery}") from exc
    issues = validate_session(session)
    if issues:
        raise DinProjectBundleError(
            f"DIN project recovery validation failed: {recovery}: "
            + "; ".join(issue.message for issue in issues)
        )
    return session, log, project_id, migration_required, user_management


def recovery_status_for_projectos(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    recovery = recovery_path_for(target)
    status: dict[str, Any] = {
        "path": str(recovery),
        "available": recovery.exists(),
        "valid": None,
        "can_recover": False,
        "error": None,
        "metadata": {
            "source_path": str(target),
            "recovery_path": str(recovery),
            "bundle_version": None,
            "project_id": None,
            "user_management_present": False,
        },
    }
    if not recovery.exists():
        return status
    try:
        raw = _load_json(recovery)
        if isinstance(raw, dict):
            status["metadata"]["bundle_version"] = raw.get("version")
            status["metadata"]["project_id"] = raw.get("project_id")
            status["metadata"]["user_management_present"] = "user_management" in raw
        session, _, _, _, _ = load_projectos_bundle_details(recovery)
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
