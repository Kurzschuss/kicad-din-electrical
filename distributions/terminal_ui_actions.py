"""UI actions for editing terminal labels and terminal rail names."""
from .terminal_editing import update_terminal_label


def rename_terminal_rail(terminals: list[dict], old_rail: str, new_rail: str) -> list[dict]:
    new_rail = str(new_rail).strip()
    if not new_rail:
        raise ValueError("new_rail must not be empty")
    result = []
    for terminal in terminals:
        item = dict(terminal)
        if item.get("terminal_rail") == old_rail:
            item["terminal_rail"] = new_rail
            if not item.get("custom_terminal_label"):
                item.pop("terminal_label", None)
        result.append(item)
    return result


def edit_terminal(terminals: list[dict], index: int, label: str | None = None) -> list[dict]:
    return update_terminal_label(terminals, index, label)
