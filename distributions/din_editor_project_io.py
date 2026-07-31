"""Legacy single-session project I/O with safe, atomic persistence."""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from .din_editor_serialization import export_session, import_session
from .din_editor_session import DinEditorSession
from .din_editor_project_bundle import DinProjectBundleError


def save_project(session: DinEditorSession, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(export_session(session), indent=2, ensure_ascii=False) + "\n"
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
        temporary.replace(target)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except (UnboundLocalError, OSError):
            pass
        raise DinProjectBundleError(f"DIN project file cannot be saved: {target}") from exc
    return target


def load_project(path: str | Path) -> DinEditorSession:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DinProjectBundleError(f"DIN project file not found: {source}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise DinProjectBundleError(f"DIN project file cannot be read: {source}") from exc
    except json.JSONDecodeError as exc:
        raise DinProjectBundleError(f"DIN project file contains invalid JSON: {source}") from exc
    try:
        return import_session(data)
    except (TypeError, ValueError, KeyError) as exc:
        raise DinProjectBundleError(f"invalid DIN editor session data: {source}") from exc
