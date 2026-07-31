"""High-level commands used by a DIN rail editor UI."""
from .din_catalog_layout_controller import add_device_and_refresh
from .terminal_layout_controller import add_terminal_and_refresh
from .din_layout_editor_view import move_and_refresh


def add_device(components: list[dict], device: dict, rails: int = 18, te_per_rail: int = 12) -> dict:
    return add_device_and_refresh(components, device, rails, te_per_rail)


def add_terminal(components: list[dict], terminal: dict, reference: str, label: str | None = None, rails: int = 18, te_per_rail: int = 12) -> dict:
    return add_terminal_and_refresh(components, terminal, reference, label, rails, te_per_rail)


def move_device(components: list[dict], index: int, rail: int, start_te: int, rails: int = 18, te_per_rail: int = 12) -> dict:
    return move_and_refresh(components, index, rail, start_te, rails, te_per_rail)
