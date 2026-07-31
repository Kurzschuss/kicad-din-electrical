"""Legacy single-session project I/O compatibility layer."""
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError, _load_json, _save_json_atomic
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession


def save_project(session: DinEditorSession, path: str | Path) -> Path:
    """Persist the legacy session using the shared atomic JSON writer."""
    return _save_json_atomic(export_session(session), path)


def load_project(path: str | Path) -> DinEditorSession:
    """Load the legacy session format using the shared JSON reader."""
    source = Path(path)
    data = _load_json(source)
    try:
        return import_session(data)
    except (TypeError, ValueError, KeyError) as exc:
        raise DinProjectBundleError(f"invalid DIN editor session data: {source}") from exc


__all__ = ["DinProjectBundleError", "load_project", "save_project"]
