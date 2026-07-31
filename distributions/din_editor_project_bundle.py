"""Combined DIN editor project state including synchronization audit history."""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def export_project_bundle(session: DinEditorSession, sync_log: DinSyncLog | None = None) -> dict:
    return {
        "version": 2,
        "session": export_session(session),
        "sync_log": (sync_log or DinSyncLog()).export(),
    }


def import_project_bundle(data: dict) -> tuple[DinEditorSession, DinSyncLog]:
    if int(data.get("version", 1)) != 2:
        raise ValueError("unsupported DIN editor project bundle version")
    session = import_session(data.get("session", {}))
    log = DinSyncLog()
    entries = data.get("sync_log", [])
    if not isinstance(entries, list):
        raise ValueError("invalid DIN synchronization log in project bundle")
    log.entries = [dict(entry) for entry in entries]
    return session, log


def save_project_bundle(session: DinEditorSession, sync_log: DinSyncLog | None, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(export_project_bundle(session, sync_log), indent=2, ensure_ascii=False) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
    temporary.replace(target)
    return target


def load_project_bundle(path: str | Path) -> tuple[DinEditorSession, DinSyncLog]:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    return import_project_bundle(data)
