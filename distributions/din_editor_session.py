"""GUI-independent session model for interactive DIN rail editing."""
from .din_editor_ui_model import editor_rows, edit_position, edit_terminal_label
from .din_rail_view import build_rail_view
from .din_rail_layout import validate_rail_layout


class DinEditorSession:
    def __init__(self, components: list[dict] | None = None, rails: int = 18, te_per_rail: int = 12):
        self.components = [dict(c) for c in (components or [])]
        self.rails = int(rails)
        self.te_per_rail = int(te_per_rail)

    def state(self) -> dict:
        errors = validate_rail_layout(self.components)
        return {
            "rows": editor_rows(self.components),
            "rails": build_rail_view(self.components, self.rails, self.te_per_rail),
            "valid": not errors,
            "errors": errors,
        }

    def move(self, index: int, rail: int, start_te: int) -> dict:
        self.components = edit_position(self.components, index, rail, start_te)["components"]
        return self.state()

    def set_terminal_label(self, index: int, label: str) -> dict:
        self.components = edit_terminal_label(self.components, index, label)
        return self.state()
