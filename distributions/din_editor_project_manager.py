"""Project manager for combined DIN layout and synchronization history."""
from copy import deepcopy
from pathlib import Path
from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_project_bundle import load_project_bundle, save_project_bundle
from .din_editor_session import DinEditorSession
from .din_editor_sync_actions import DinEditorSyncActions
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session, ValidationIssue


class DinEditorProjectManager:
    def __init__(self, session: DinEditorSession | None = None, sync_log: DinSyncLog | None = None):
        self.session = session or DinEditorSession()
        self.sync_log = sync_log or DinSyncLog()
        self.history = DinEditorHistory(self.session, self.sync_log)
        self.path: Path | None = None
        self._saved_state = self._snapshot()
        self.dirty = False
        self.change_service = self._build_change_service()

    def _snapshot(self) -> dict:
        return {"components": deepcopy(self.session.components), "sync_log": deepcopy(self.sync_log.entries)}

    @staticmethod
    def _snapshot_for(session: DinEditorSession, sync_log: DinSyncLog) -> dict:
        return {"components": deepcopy(session.components), "sync_log": deepcopy(sync_log.entries)}

    def _prepare_project_state(
        self,
        session: DinEditorSession,
        sync_log: DinSyncLog,
    ) -> tuple[DinEditorHistory, DinEditorChangeService, dict]:
        history = DinEditorHistory(session, sync_log)
        change_service = DinEditorChangeService(
            session,
            history,
            on_change=self._refresh_dirty,
        )
        saved_state = self._snapshot_for(session, sync_log)
        return history, change_service, saved_state

    def _refresh_dirty(self) -> None:
        self.dirty = self._snapshot() != self._saved_state

    def _build_change_service(self) -> DinEditorChangeService:
        return DinEditorChangeService(self.session, self.history, on_change=self._refresh_dirty)

    def sync_actions(self, view_model) -> DinEditorSyncActions:
        sync_service = getattr(view_model, "sync_service", None)
        if sync_service is None or sync_service.change_service is not self.change_service:
            raise ValueError("sync view model is not bound to this project manager")
        return DinEditorSyncActions(view_model, self.sync_log, on_change=self._refresh_dirty)

    @property
    def has_unsaved_changes(self) -> bool:
        self._refresh_dirty()
        return self.dirty

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
        _, _, saved_state = self._prepare_project_state(
            self.session,
            self.sync_log,
        )
        result = save_project_bundle(self.session, self.sync_log, target)
        self.path = result
        self._saved_state = saved_state
        self.dirty = False
        self.history.clear()
        return result

    def load(self, path: str | Path, *, discard_changes: bool = False) -> DinEditorSession:
        if self.has_unsaved_changes and not discard_changes:
            raise RuntimeError("project has unsaved changes; save or discard them before loading")
        session, sync_log = load_project_bundle(path)
        history, change_service, saved_state = self._prepare_project_state(session, sync_log)
        self.session = session
        self.sync_log = sync_log
        self.history = history
        self.change_service = change_service
        self.path = Path(path)
        self._saved_state = saved_state
        self.dirty = False
        return self.session

    def new_project(self, *, discard_changes: bool = False) -> DinEditorSession:
        if self.has_unsaved_changes and not discard_changes:
            raise RuntimeError("project has unsaved changes; save or discard them before creating a new project")
        session = DinEditorSession()
        sync_log = DinSyncLog()
        history, change_service, saved_state = self._prepare_project_state(session, sync_log)
        self.session = session
        self.sync_log = sync_log
        self.history = history
        self.change_service = change_service
        self.path = None
        self._saved_state = saved_state
        self.dirty = False
        return self.session

    def discard_changes(self) -> None:
        if not self.has_unsaved_changes:
            return
        if self.path is None:
            self.new_project(discard_changes=True)
            return
        session, sync_log = load_project_bundle(self.path)
        history, change_service, saved_state = self._prepare_project_state(session, sync_log)
        self.session = session
        self.sync_log = sync_log
        self.history = history
        self.change_service = change_service
        self._saved_state = saved_state
        self.dirty = False

    def state(self) -> dict:
        issues = self.validate()
        dirty = self.has_unsaved_changes
        return {
            "path": str(self.path) if self.path else None,
            "dirty": dirty,
            "has_unsaved_changes": dirty,
            "valid": not issues,
            "validation_issues": [issue.__dict__ for issue in issues],
            "history": self.history.state(),
            "session": self.session.state(),
            "sync_log_entries": len(self.sync_log.entries),
        }
