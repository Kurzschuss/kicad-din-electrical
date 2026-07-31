"""UI model for editing DIN positions and terminal labels."""
from .din_editor_commands import move_device
from .terminal_catalog_editor import add_terminal


def component_editor_row(component: dict, index: int) -> dict:
    return {
        "index": index,
        "reference": component.get("reference", ""),
        "value": component.get("value", ""),
        "rail": int(component.get("rail", 1)),
        "start_te": int(component.get("start_te", 1)),
        "end_te": int(component.get("end_te", component.get("start_te", 1))),
        "width_te": int(component.get("width_te", component.get("te", 1))),
        "label": component.get("label") or component.get("terminal_label") or "",
        "editable_label": bool(component.get("can_edit_label", component.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK")),
    }


def editor_rows(components: list[dict]) -> list[dict]:
    return [component_editor_row(component, index) for index, component in enumerate(components)]


def edit_position(components: list[dict], index: int, rail: int, start_te: int) -> dict:
    return move_device(components, index, rail, start_te)


def edit_terminal_label(components: list[dict], index: int, label: str) -> list[dict]:
    if index < 0 or index >= len(components):
        raise IndexError("component index out of range")
    result = [dict(c) for c in components]
    if result[index].get("component_type") != "DIN_RAIL_TERMINAL_BLOCK":
        raise ValueError("only terminal blocks have editable terminal labels")
    value = str(label).strip()
    if not value:
        raise ValueError("terminal label must not be empty")
    result[index]["label"] = value
    result[index]["terminal_label"] = value
    result[index]["can_edit_label"] = True
    return result
