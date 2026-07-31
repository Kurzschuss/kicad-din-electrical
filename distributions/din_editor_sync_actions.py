"""High-level actions for synchronizing a DIN editor with KiCad."""
from .din_editor_sync_view_model import DinEditorSyncViewModel
from .din_editor_sync_log import DinSyncLog


class DinEditorSyncActions:
    def __init__(self, view_model: DinEditorSyncViewModel, sync_log: DinSyncLog | None = None):
        self.view_model = view_model
        self.sync_log = sync_log or DinSyncLog()

    def inspect(self, kicad_fields: list[dict] | None = None) -> dict:
        return self.view_model.refresh(kicad_fields)

    def keep_din(self, reference: str) -> dict:
        state = self.view_model.choose(reference, "local")
        self.sync_log.record(reference, "DIN", self._label(reference), "kept")
        return state

    def use_kicad(self, reference: str) -> dict:
        state = self.view_model.choose(reference, "kicad")
        self.sync_log.record(reference, "KiCad", self._label(reference), "imported")
        return state

    def resolve_all(self, choice: str) -> dict:
        state = self.view_model.refresh()
        for conflict in list(state.get("conflicts", [])):
            self.view_model.choose(str(conflict["reference"]), choice)
            source = "KiCad" if choice == "kicad" else "DIN"
            action = "imported" if choice == "kicad" else "kept"
            self.sync_log.record(str(conflict["reference"]), source, self._label(str(conflict["reference"])), action)
        return self.view_model.refresh()

    def _label(self, reference: str) -> str:
        for component in self.view_model.sync_service.session.components:
            if str(component.get("reference", "")) == str(reference):
                return str(component.get("label") or component.get("terminal_label") or "")
        return ""
