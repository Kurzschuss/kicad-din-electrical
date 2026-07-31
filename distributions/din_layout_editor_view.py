"""Controller-friendly model for an interactive 18 x 12-TE DIN editor."""
from .din_rail_view import build_rail_view
from .din_layout_editor import move_component, validate_layout


def build_editor_state(components: list[dict], rails: int = 18, te_per_rail: int = 12) -> dict:
    validation = validate_layout(components, rails, te_per_rail)
    return {
        "rails": build_rail_view(validation["components"], rails, te_per_rail),
        "components": validation["components"],
        "valid": validation["valid"],
    }


def move_and_refresh(components: list[dict], index: int, rail: int, start_te: int, rails: int = 18, te_per_rail: int = 12) -> dict:
    moved = move_component(components, index, rail, start_te, rails, te_per_rail)
    return build_editor_state(moved, rails, te_per_rail)
