"""Project manager for combined DIN layout, synchronization history and ProjectOS state."""
from copy import deepcopy
from pathlib import Path
from uuid import UUID, uuid4

from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_project_bundle import recovery_path_for
from .din_editor_session import DinEditorSession
from .din_editor_sync_actions import DinEditorSyncActions
from .din_editor_sync_log import DinSyncLog
from .din_editor_validation import validate_session, ValidationIssue
from .projectos_project_bundle_v4 import (
    empty_user_management,
    load_projectos_bundle_details,
    load_projectos_recovery_details,
    recovery_status_for_projectos,
    save_projectos_bundle,
)
from .projectos_user_management_persistence import ProjectOSUserManagementState


def _new_project_id() -> str:
    return str(uuid4())


def _normalize_project_id(value: str) -> str:
    return str(UUID(value))


class DinEditorProjectManager:
    def __init__(
        self,
        session: DinEditorSession | None = None,
        sync_log: DinSyncLog | None = None,
        *,
        project_id: str | None = None,
        user_management: ProjectOSUserManagementState | None = None,
    ):
        self.session = session or DinEditorSession()
        self.sync_log = sync_log or DinSyncLog()
        self.project_id = _normalize_project_id(project_id) if project_id is not None else _new_project_id()
        self.user_management = user_management or empty_user_management(self.project_id)
        if self.user_management.project_id != self.project_id:
            raise ValueError("user management belongs to another project")
        self.project_identity_migration_pending = False
        self.history = DinEditorHistory(self.session, self.sync_log)
        self.path: Path | None = None
        self._saved_state = self._snapshot()
        self._recovered_from: Path | None = None
        self.dirty = False
        self.change_service = self._build_change_service()

    def _snapshot(self) -> dict:
        return {
            "components": deepcopy(self.session.components),
            "sync_log": deepcopy(self.sync_log.entries),
            "user_management": deepcopy(self.user_management.as_dict()),
        }

    @staticmethod
    def _snapshot_for(
        session: DinEditorSession,
        sync_log: DinSyncLog,
        user_management: ProjectOSUserManagementState,
    ) -> dict:
        return {
            "components": deepcopy(session.components),
            "sync_log": deepcopy(sync_log.entries),
            "user_management": deepcopy(user_management.as_dict()),
        }

    def _prepare_project_state(
        self,
        session: DinEditorSession,
        sync_log: DinSyncLog,
        user_management: ProjectOSUserManagementState,
    ) -> tuple[DinEditorHistory, DinEditorChangeService, dict]:
        history = DinEditorHistory(session, sync_log)
        change_service = DinEditorChangeService(
            session,
            history,
            on_change=self._refresh_dirty,
        )
        saved_state = self._snapshot_for(session, sync_log, user_management)
        return history, change_service, saved_state

    def _refresh_dirty(self) -> None:
        self.dirty = (
            self._snapshot() != self._saved_state
            or self._recovered_from is not None
            or self.project_identity_migration_pending
        )

    def _build_change_service(self) -> DinEditorChangeService:
        return DinEditorChangeService(self.session, self.history, on_change=self._refresh_dirty)

    def _commit_user_management_change(self, state: ProjectOSUserManagementState) -> None:
        """Interner Commit-Pfad für bereits vollständig validierte Fachänderungen."""
        if state.project_id != self.project_id:
            raise ValueError("user management belongs to another project")
        self.user_management = state
        self._refresh_dirty()

    def set_user_management(self, state: ProjectOSUserManagementState) -> None:
        """Kompatibilitätspfad für explizite Zustandssetzung und Tests.

        Reguläre fachliche Änderungen müssen über ProjectOSUserManagementChangeService
        laufen, damit Atomarität sowie Audit-/Bus-Hooks nicht umgangen werden.
        """
        self._commit_user_management_change(state)

    def sync_actions(self, view_model) -> DinEditorSyncActions:
        sync_service = getattr(view_model, "sync_service", None)
        if sync_service is None or sync_service.change_service is not self.change_service:
            raise ValueError("sync view model is not bound to this project manager")
        bound_change_service = self.change_service
        bound_sync_log = self.sync_log
        return DinEditorSyncActions(
            view_model,
            bound_sync_log,
            on_change=self._refresh_dirty,
            is_current=lambda: (
                self.change_service is bound_change_service
                and self.sync_log is bound_sync_log
            ),
            project_id=self.project_id,
        )

    @property
    def has_unsaved_changes(self) -> bool:
        self._refresh_dirty()
        return self.dirty

    def mark_dirty(self) -> None:
        self.dirty = True

    def validate(self) -> list[ValidationIssue]:
        return validate_session(self.session)

    def recovery_status(self, path: str | Path | None = None) -> dict:
        target = Path(path) if path is not None else self.path
        if target is None:
            return {
                "path": None,
                "available": False,
                "valid": None,
                "can_recover": False,
                "error": None,
                "metadata": {
                    "source_path": None,
                    "recovery_path": None,
                    "bundle_version": None,
                    "project_id": None,
                    "user_management_present": False,
                },
            }
        return recovery_status_for_projectos(target)

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
            self.user_management,
        )
        result = save_projectos_bundle(
            self.session,
            self.sync_log,
            target,
            project_id=self.project_id,
            user_management=self.user_management,
        )
        self.path = result
        self._saved_state = saved_state
        self._recovered_from = None
        self.project_identity_migration_pending = False
        self.dirty = False
        self.history.clear()
        return result

    def load(self, path: str | Path, *, discard_changes: bool = False) -> DinEditorSession:
        if self.has_unsaved_changes and not discard_changes:
            raise RuntimeError("project has unsaved changes; save or discard them before loading")
        session, sync_log, project_id, migration_required, user_management = load_projectos_bundle_details(path)
        resolved_project_id = project_id or _new_project_id()
        resolved_user_management = user_management or empty_user_management(resolved_project_id)
        history, change_service, saved_state = self._prepare_project_state(
            session, sync_log, resolved_user_management
        )
        self.session = session
        self.sync_log = sync_log
        self.user_management = resolved_user_management
        self.history = history
        self.change_service = change_service
        self.path = Path(path)
        self.project_id = resolved_project_id
        self.project_identity_migration_pending = migration_required
        self._saved_state = saved_state
        self._recovered_from = None
        self.dirty = migration_required
        return self.session

    def recover(self, path: str | Path | None = None, *, discard_changes: bool = False) -> DinEditorSession:
        if self.has_unsaved_changes and not discard_changes:
            raise RuntimeError("project has unsaved changes; save or discard them before recovery")
        target = Path(path) if path is not None else self.path
        if target is None:
            raise ValueError("project path is not set")
        session, sync_log, project_id, migration_required, user_management = load_projectos_recovery_details(target)
        resolved_project_id = project_id or _new_project_id()
        resolved_user_management = user_management or empty_user_management(resolved_project_id)
        history, change_service, saved_state = self._prepare_project_state(
            session, sync_log, resolved_user_management
        )
        self.session = session
        self.sync_log = sync_log
        self.user_management = resolved_user_management
        self.history = history
        self.change_service = change_service
        self.path = target
        self.project_id = resolved_project_id
        self.project_identity_migration_pending = migration_required
        self._saved_state = saved_state
        self._recovered_from = recovery_path_for(target)
        self.dirty = True
        return self.session

    def new_project(self, *, discard_changes: bool = False) -> DinEditorSession:
        if self.has_unsaved_changes and not discard_changes:
            raise RuntimeError("project has unsaved changes; save or discard them before creating a new project")
        session = DinEditorSession()
        sync_log = DinSyncLog()
        project_id = _new_project_id()
        user_management = empty_user_management(project_id)
        history, change_service, saved_state = self._prepare_project_state(
            session, sync_log, user_management
        )
        self.session = session
        self.sync_log = sync_log
        self.user_management = user_management
        self.history = history
        self.change_service = change_service
        self.path = None
        self.project_id = project_id
        self.project_identity_migration_pending = False
        self._saved_state = saved_state
        self._recovered_from = None
        self.dirty = False
        return self.session

    def discard_changes(self) -> None:
        if not self.has_unsaved_changes:
            return
        if self.path is None:
            self.new_project(discard_changes=True)
            return
        session, sync_log, project_id, migration_required, user_management = load_projectos_bundle_details(self.path)
        resolved_project_id = project_id or _new_project_id()
        resolved_user_management = user_management or empty_user_management(resolved_project_id)
        history, change_service, saved_state = self._prepare_project_state(
            session, sync_log, resolved_user_management
        )
        self.session = session
        self.sync_log = sync_log
        self.user_management = resolved_user_management
        self.history = history
        self.change_service = change_service
        self.project_id = resolved_project_id
        self.project_identity_migration_pending = migration_required
        self._saved_state = saved_state
        self._recovered_from = None
        self.dirty = migration_required

    def state(self) -> dict:
        issues = self.validate()
        dirty = self.has_unsaved_changes
        return {
            "project_id": self.project_id,
            "project_identity_migration_pending": self.project_identity_migration_pending,
            "path": str(self.path) if self.path else None,
            "dirty": dirty,
            "has_unsaved_changes": dirty,
            "recovered_from": str(self._recovered_from) if self._recovered_from else None,
            "recovery": self.recovery_status(),
            "valid": not issues,
            "validation_issues": [issue.__dict__ for issue in issues],
            "history": self.history.state(),
            "session": self.session.state(),
            "sync_log_entries": len(self.sync_log.entries),
            "user_management": self.user_management.as_dict(),
        }
