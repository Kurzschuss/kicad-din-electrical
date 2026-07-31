"""Add DIN rail terminal blocks from the terminal catalog and auto-place them."""
from .din_rail_auto_place import find_free_position
from .terminal_catalog import generic_terminal_catalog, terminal_block


def terminal_choices() -> list[dict]:
    return [dict(item) for item in generic_terminal_catalog()]


def add_terminal(components: list[dict], terminal: dict, reference: str, label: str | None = None, rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    reference = str(reference).strip()
    if not reference:
        raise ValueError("terminal reference is required")
    if any(str(item.get("reference")) == reference for item in components):
        raise ValueError(f"reference already exists: {reference}")
    item = dict(terminal)
    item["reference"] = reference
    item["label"] = str(label).strip() if label is not None else str(terminal.get("terminal_function") or reference)
    item["terminal_label"] = item["label"]
    item["can_edit_label"] = True
    width = int(item.get("width_te", 1))
    rail, start = find_free_position(components, width, rails, te_per_rail)
    item.update({"rail": rail, "start_te": start, "end_te": start + width - 1})
    return [*components, item]


def new_terminal(part_number: str, manufacturer: str, reference: str, label: str, width_te: int = 1, connection_count: int = 2) -> dict:
    return add_terminal([], terminal_block(part_number, manufacturer, width_te, connection_count), reference, label)[0]
