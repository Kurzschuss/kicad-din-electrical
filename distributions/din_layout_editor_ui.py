"""UI-facing actions for the DIN rail editor."""
from .din_layout_editor import move_component, validate_layout
from .terminal_label_manager import set_terminal_label


def edit_component_position(components: list[dict], index: int, rail: int, start_te: int) -> dict:
    updated = move_component(components, index, rail, start_te)
    validation = validate_layout(updated)
    return {"components": updated, "valid": validation["valid"]}


def edit_terminal_label(terminals: list[dict], index: int, label: str) -> list[dict]:
    if index < 0 or index >= len(terminals):
        raise IndexError("terminal index out of range")
    result = [dict(t) for t in terminals]
    result[index] = set_terminal_label(result[index], label)
    return result
