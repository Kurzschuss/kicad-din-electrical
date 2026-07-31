"""Project-file I/O for DIN editor sessions."""
import json
from pathlib import Path
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession


def save_project(session: DinEditorSession, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(export_session(session), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def load_project(path: str | Path) -> DinEditorSession:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    return import_session(data)
