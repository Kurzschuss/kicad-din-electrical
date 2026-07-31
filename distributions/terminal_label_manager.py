"""Editable terminal labels with stable electrical identity."""


def set_terminal_label(terminal: dict, label: str) -> dict:
    """Change only the human-facing label; keep reference and wiring intact."""
    value = str(label).strip()
    if not value:
        raise ValueError("terminal label must not be empty")
    updated = dict(terminal)
    updated["label"] = value
    updated["terminal_label"] = value
    updated["can_edit_label"] = True
    return updated


def rename_terminal(terminals: list[dict], reference: str, label: str) -> list[dict]:
    updated = []
    found = False
    for terminal in terminals:
        item = dict(terminal)
        if str(item.get("reference")) == str(reference):
            item = set_terminal_label(item, label)
            found = True
        updated.append(item)
    if not found:
        raise KeyError(f"unknown terminal reference: {reference}")
    return updated
