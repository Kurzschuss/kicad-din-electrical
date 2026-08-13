"""GUI-neutral workflow view model for DIN editor project and KiCad sync actions."""
from copy import deepcopy
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


class DinEditorWorkflowViewModel:
    """Bind project, edit, persistence and synchronization actions for a GUI."""

    def __init__(self, manager: DinEditorProjectManager | None = None):
        self.manager = manager or DinEditorProjectManager()
        self._busy = False
        self._error: dict | None = None
        self._message: str | None = None
        self._last_operation: str | None = None
        self._conflicts: list[dict] = []
        self._bind_sync()

    def _bind_sync(self) -> None:
        self.sync_view_model = DinEditorSyncViewModel(
            DinEditorSyncService(self.manager.change_service)
        )
        self.sync_actions = self.manager.sync_actions(self.sync_view_model)
        self._conflicts = []

    def _capture_sync_state(self, state: dict) -> None:
        self._conflicts = deepcopy(state.get("conflicts", []))

    def _refresh_sync_state(self, _result=None) -> None:
        self._capture_sync_state(self.sync_view_model.refresh())

    def _run(
        self,
        operation: str,
        action,
        *,
        message: str | None = None,
        on_success=None,
    ) -> dict:
        if self._busy:
            self._error = {
                "operation": operation,
                "type": "RuntimeError",
                "message": "another workflow operation is already running",
            }
            return self.state()

        self._busy = True
        self._error = None
        self._message = None
        self._last_operation = operation
        try:
            result = action()
            if on_success is not None:
                on_success(result)
            self._message = message
        except Exception as exc:
            self._error = {
                "operation": operation,
                "type": type(exc).__name__,
                "message": str(exc),
            }
        finally:
            self._busy = False
        return self.state()

    def clear_feedback(self) -> dict:
        self._error = None
        self._message = None
        return self.state()

    def new_project(self, *, discard_changes: bool = False) -> dict:
        return self._run(
            "new",
            lambda: self.manager.new_project(discard_changes=discard_changes),
            message="New project created",
            on_success=lambda _result: self._bind_sync(),
        )

    def open_project(
        self,
        path: str | Path,
        *,
        discard_changes: bool = False,
    ) -> dict:
        target = Path(path)
        return self._run(
            "open",
            lambda: self.manager.load(target, discard_changes=discard_changes),
            message=f"Project opened: {target}",
            on_success=lambda _result: self._bind_sync(),
        )

    def save(self) -> dict:
        return self._run(
            "save",
            self.manager.save,
            message="Project saved",
        )

    def save_as(self, path: str | Path) -> dict:
        target = Path(path)
        return self._run(
            "save_as",
            lambda: self.manager.save(target),
            message=f"Project saved as: {target}",
        )

    def discard_changes(self) -> dict:
        return self._run(
            "discard",
            self.manager.discard_changes,
            message="Unsaved changes discarded",
            on_success=lambda _result: self._bind_sync(),
        )

    def set_terminal_label(self, index: int, label: str) -> dict:
        return self._run(
            "edit_terminal_label",
            lambda: self.manager.change_service.set_terminal_label(index, label),
            message="Terminal label changed",
            on_success=self._refresh_sync_state,
        )

    def move_component(self, index: int, rail: int, start_te: int) -> dict:
        return self._run(
            "move_component",
            lambda: self.manager.change_service.move(index, rail, start_te),
            message="Component moved",
            on_success=self._refresh_sync_state,
        )

    def undo(self) -> dict:
        return self._run(
            "undo",
            self.manager.change_service.undo,
            message="Change undone",
            on_success=self._refresh_sync_state,
        )

    def redo(self) -> dict:
        return self._run(
            "redo",
            self.manager.change_service.redo,
            message="Change redone",
            on_success=self._refresh_sync_state,
        )

    def inspect_sync(self, kicad_fields: list[dict] | None = None) -> dict:
        return self._run(
            "sync_inspect",
            lambda: self.sync_actions.inspect(kicad_fields),
            message="KiCad synchronization inspected",
            on_success=self._capture_sync_state,
        )

    def keep_din(self, reference: str) -> dict:
        return self._run(
            "sync_keep_din",
            lambda: self.sync_actions.keep_din(reference),
            message=f"Kept DIN value for {reference}",
            on_success=self._capture_sync_state,
        )

    def use_kicad(self, reference: str) -> dict:
        return self._run(
            "sync_use_kicad",
            lambda: self.sync_actions.use_kicad(reference),
            message=f"Accepted KiCad value for {reference}",
            on_success=self._capture_sync_state,
        )

    def resolve_all(self, choice: str) -> dict:
        return self._run(
            "sync_resolve_all",
            lambda: self.sync_actions.resolve_all(choice),
            message=f"Synchronization conflicts resolved with {choice}",
            on_success=self._capture_sync_state,
        )

    def import_manifest(self, manifest: dict, *, overwrite: bool = True) -> dict:
        return self._run(
            "sync_import_manifest",
            lambda: self.sync_actions.import_manifest(manifest, overwrite=overwrite),
            message="KiCad manifest imported",
            on_success=self._refresh_sync_state,
        )

    def state(self) -> dict:
        project = self.manager.state()
        history = project["history"]
        idle = not self._busy
        return {
            "busy": self._busy,
            "error": deepcopy(self._error),
            "message": self._message,
            "last_operation": self._last_operation,
            "project_id": project["project_id"],
            "path": project["path"],
            "dirty": project["dirty"],
            "unsaved_changes": project["has_unsaved_changes"],
            "save_as_required": project["path"] is None,
            "conflicts": deepcopy(self._conflicts),
            "sync_conflict_count": len(self._conflicts),
            "actions": {
                "can_new": idle,
                "can_open": idle,
                "can_save": idle and project["path"] is not None,
                "can_save_as": idle,
                "can_sync": idle,
                "can_resolve_conflicts": idle and bool(self._conflicts),
                "can_undo": idle and bool(history["can_undo"]),
                "can_redo": idle and bool(history["can_redo"]),
                "can_discard": idle and project["has_unsaved_changes"],
            },
            "project": project,
        }
