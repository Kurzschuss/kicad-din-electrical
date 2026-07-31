"""Legacy single-session project I/O compatibility layer."""
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError, load_project_bundle, save_project_bundle
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def save_project(session: DinEditorSession, path: str | Path) -> Path:
    """Persist a legacy session using the same atomic writer as project bundles."""
    return save_project_bundle(session, DinSyncLog(), path)


def load_project(path: str | Path) -> DinEditorSession:
    """Load a legacy session while ignoring an empty synchronization history."""
    session, _sync_log = load_project_bundle(path)
    return session


__all__ = ["DinProjectBundleError", "load_project", "save_project"]
