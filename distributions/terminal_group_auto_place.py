"""Arrange terminal groups on DIN rails without moving unrelated components."""
from .din_rail_auto_place import find_free_position
from .din_rail_layout import component_te, validate_rail_layout
from .terminal_grouping import group_terminals


def auto_place_terminal_groups(components: list[dict], rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    result = [dict(c) for c in components]
    terminals = [c for c in result if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK"]
    for group in group_terminals(terminals):
        group_sorted = sorted(group, key=lambda item: (int(item.get("rail", 1)), int(item.get("start_te", 1)), str(item.get("reference", ""))))
        preferred_rail = None
        preferred_start = None
        for terminal in group_sorted:
            reference = str(terminal.get("reference"))
            target = next(c for c in result if str(c.get("reference")) == reference)
            width = component_te(target)
            others = [c for c in result if str(c.get("reference")) != reference]
            if preferred_rail is not None and preferred_start is not None and preferred_start + width - 1 <= int(te_per_rail):
                rail, start = preferred_rail, preferred_start
            else:
                rail, start = find_free_position(others, width, rails, te_per_rail)
            target.update({"rail": rail, "start_te": start, "end_te": start + width - 1, "width_te": width})
            preferred_rail = rail
            preferred_start = start + width
    errors = validate_rail_layout(result)
    if errors:
        raise ValueError("terminal grouping produced an invalid layout: " + "; ".join(errors))
    return result
