"""Apply user edits to terminal labels while preserving generated defaults."""
from .terminal_labels import terminal_label
from .terminal_validation import validate_terminal_labels


def update_terminal_label(terminals: list[dict], index: int, new_label: str | None) -> list[dict]:
    if index < 0 or index >= len(terminals):
        raise IndexError("terminal index out of range")
    result = [dict(t) for t in terminals]
    item = result[index]
    value = (new_label or "").strip()
    if value:
        item["custom_terminal_label"] = value
        item["terminal_label"] = value
    else:
        item.pop("custom_terminal_label", None)
        item["terminal_label"] = terminal_label(
            item.get("terminal_rail", "X1"),
            int(item.get("terminal_number", index + 1)),
        )
    return validate_terminal_labels(result)
