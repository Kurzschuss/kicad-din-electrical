"""High-level actions for synchronizing a DIN editor with KiCad."""
from .din_editor_sync_view_model import DinEditorSyncViewModel
from .din_editor_sync_log import DinSyncLog


class DinEditorSyncActions:
    def __init__(
        self,
        view_model: DinEditorSyncViewModel,
        sync_log: DinSyncLog | None = None,
        on_change=None,
        is_current=None,
    ):
        self.view_model = view_model
        self.sync_log = sync_log or DinSyncLog()
        self.on_change = on_change
        self.is_current = is_current

    def _ensure_current(self) -> None:
        if self.is_current is not None and not self.is_current():
            raise RuntimeError("synchronization actions are no longer bound to the active project")

    def _changed(self, state: dict) -> dict:
        if self.on_change is not None:
            self.on_change()
        return state

    def _rollback_history(self, history, captured) -> None:
        history.restore(captured)
        if self.on_change is not None:
            self.on_change()

    def inspect(self, kicad_fields: list[dict] | None = None) -> dict:
        self._ensure_current()
        return self.view_model.refresh(kicad_fields)

    def keep_din(self, reference: str) -> dict:
        self._ensure_current()
        history = self.view_model.sync_service.change_service.history
        captured = history.capture()
        try:
            history.checkpoint()
            state = self.view_model.choose(reference, "local")
            self.sync_log.record(reference, "DIN", self._label(reference), "kept")
        except Exception:
            self._rollback_history(history, captured)
            raise
        return self._changed(state)

    def use_kicad(self, reference: str) -> dict:
        self._ensure_current()
        history = self.view_model.sync_service.change_service.history
        captured = history.capture()
        try:
            state = self.view_model.choose(reference, "kicad")
            self.sync_log.record(reference, "KiCad", self._label(reference), "imported")
        except Exception:
            self._rollback_history(history, captured)
            raise
        return self._changed(state)

    def import_manifest(self, manifest: dict, overwrite: bool = True) -> dict:
        self._ensure_current()
        history = self.view_model.sync_service.change_service.history
        captured = history.capture()
        before = {
            str(component.get("reference", "")): str(component.get("label") or component.get("terminal_label") or "")
            for component in self.view_model.sync_service.session.components
        }
        try:
            state = self.view_model.sync_service.import_manifest_labels(manifest, overwrite=overwrite)
            after = self.view_model.sync_service.session.components
            for component in after:
                reference = str(component.get("reference", ""))
                label = str(component.get("label") or component.get("terminal_label") or "")
                if reference in before and label != before[reference]:
                    self.sync_log.record(reference, "KiCad", label, "imported")
        except Exception:
            self._rollback_history(history, captured)
            raise
        return self._changed(state)

    def resolve_all(self, choice: str) -> dict:
        self._ensure_current()
        state = self.view_model.refresh()
        conflicts = list(state.get("conflicts", []))
        if not conflicts:
            return state
        history = self.view_model.sync_service.change_service.history
        captured = history.capture()
        try:
            if choice == "local":
                history.checkpoint()
            state = self.view_model.choose_all(choice)
            source = "KiCad" if choice == "kicad" else "DIN"
            action = "imported" if choice == "kicad" else "kept"
            for conflict in conflicts:
                reference = str(conflict["reference"])
                self.sync_log.record(reference, source, self._label(reference), action)
        except Exception:
            self._rollback_history(history, captured)
            raise
        return self._changed(state)

    def _label(self, reference: str) -> str:
        for component in self.view_model.sync_service.session.components:
            if str(component.get("reference", "")) == str(reference):
                return str(component.get("label") or component.get("terminal_label") or "")
        return ""
