"""Project manager for combined DIN layout and synchronization history."""
from pathlib import Path
from .din_editor_project_bundle import load_project_bundle, save_project_bundle
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session, ValidationIssue


class DinEditorProjectManager:
    def __init__(self, session: DinEditorSession | None = None, sync_log: DinSyncLog | None = None):
        self.session = session or DinEditorSession()
        self.sync_log = sync_log or DinSyncLog()
        self.path: Path | None = None
        self.dirty = False

    def mark_dirty(self) -> None:
        self.dirty = True

    def validate(self) -> list[ValidationIssue]:
        return validate_session(self.session)

    def save(self, path: str | Path | None = None, *, validate: bool = True) -> Path:
        if validate:
            issues = self.validate()
            if issues:
                raise ValueError("DIN project validation failed: " + "; ".join(issue.message for issue in issues))
        target = Path(path) if path is not None else self.path
        if target is None:
            raise ValueError("project path is not set")
        result = save_project_bundle(self.session, self.sync_log, target)
        self.path = result
        self.dirty = False
        return result

    def load(self, path: str | Path) -> DinEditorSession:
        session, sync_log = load_project_bundle(path)
        self.session = session
        self.sync_log = sync_log
        self.path = Path(path)
        self.dirty = False
        return self.session

    def state(self) -> dict:
        issues = self.validate()
        return {
            "path": str(self.path) if self.path else None,
            "dirty": self.dirty,
            "valid": not issues,
            "validation_issues": [issue.__dict__ for issue in issues],
            "session": self.session.state(),
            "sync_log_entries": len(self.sync_log.entries),
        }
