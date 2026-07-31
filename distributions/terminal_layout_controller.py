"""Integrate editable terminal blocks with the shared DIN editor."""
from .din_layout_editor_view import build_editor_state
from .terminal_catalog_editor import add_terminal, terminal_choices


def available_terminals() -> list[dict]:
    return terminal_choices()


def add_terminal_and_refresh(components: list[dict], terminal: dict, reference: str, label: str | None = None, rails: int = 18, te_per_rail: int = 12) -> dict:
    updated = add_terminal(components, terminal, reference, label, rails, te_per_rail)
    return build_editor_state(updated, rails, te_per_rail)
