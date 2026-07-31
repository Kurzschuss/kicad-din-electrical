"""Batch editing helpers for terminal rails and labels."""
from .terminal_editing import update_terminal_label
from .terminal_ui_actions import rename_terminal_rail


def rename_rail(terminals: list[dict], old_rail: str, new_rail: str) -> list[dict]:
    return rename_terminal_rail(terminals, old_rail, new_rail)


def prefix_labels(terminals: list[dict], prefix: str) -> list[dict]:
    prefix = str(prefix).strip()
    if not prefix:
        raise ValueError("prefix must not be empty")
    result = []
    for item in terminals:
        current = str(item.get("terminal_label", item.get("terminal", "")))
        result.append({**item, "custom_terminal_label": f"{prefix}{current}"})
    return result


def clear_custom_labels(terminals: list[dict]) -> list[dict]:
    result = []
    for index, item in enumerate(terminals):
        result = update_terminal_label(result + [dict(item)], index, None)
    return result
