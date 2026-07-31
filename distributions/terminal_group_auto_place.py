"""Arrange terminal groups on DIN rails without moving unrelated components."""
from .din_rail_auto_place import find_free_position
from .din_rail_layout import component_te, validate_rail_layout
from .terminal_grouping import group_terminals


def auto_place_terminal_groups(components: list[dict], rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    result = [dict(c) for c in components]
    terminals = [c for c in result if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK"]
    non_terminals = [c for c in result if c.get("component_type") != "DIN_RAIL_TERMINAL_BLOCK"]
    for group in group_terminals(terminals):
        for terminal in group:
            reference = str(terminal.get("reference"))
            others = [c for c in non_terminals + [x for x in terminals if str(x.get("reference")) != reference] if str(c.get("reference")) != reference]
            rail, start = find_free_position(others, component_te(terminal), rails, te_per_rail)
            for item in result:
                if str(item.get("reference")) == reference:
                    item.update({"rail": rail, "start_te": start, "end_te": start + component_te(terminal) - 1, "width_te": component_te(terminal)})
                    break
    errors = validate_rail_layout(result)
    if errors:
        raise ValueError("terminal grouping produced an invalid layout: " + "; ".join(errors))
    return result
