"""High-level actions for synchronizing a DIN editor with KiCad."""
from .din_editor_sync_view_model import DinEditorSyncViewModel


class DinEditorSyncActions:
    def __init__(self, view_model: DinEditorSyncViewModel):
        self.view_model = view_model

    def inspect(self, kicad_fields: list[dict] | None = None) -> dict:
        return self.view_model.refresh(kicad_fields)

    def keep_din(self, reference: str) -> dict:
        return self.view_model.choose(reference, "local")

    def use_kicad(self, reference: str) -> dict:
        return self.view_model.choose(reference, "kicad")

    def resolve_all(self, choice: str) -> dict:
        state = self.view_model.refresh()
        for conflict in list(state.get("conflicts", [])):
            self.view_model.choose(str(conflict["reference"]), choice)
        return self.view_model.refresh()
