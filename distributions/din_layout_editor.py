"""Editable model for placing DIN devices on 12-TE rails."""
from .din_rail_layout import component_te, layout_components


def move_component(components: list[dict], index: int, rail: int, start_te: int, rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    if index < 0 or index >= len(components):
        raise IndexError("component index out of range")
    rail = int(rail); start_te = int(start_te)
    width = component_te(components[index])
    if rail < 1 or rail > rails or start_te < 1 or start_te + width - 1 > te_per_rail:
        raise ValueError("component does not fit at requested DIN position")
    result = [dict(c) for c in components]
    result[index].update({"rail": rail, "start_te": start_te, "end_te": start_te + width - 1})
    return result


def validate_layout(components: list[dict], rails: int = 18, te_per_rail: int = 12) -> dict:
    placed = layout_components(components, rails, te_per_rail)
    occupied = {(item["rail"], te): item for item in placed for te in range(item["start_te"], item["end_te"] + 1)}
    return {"valid": len(occupied) == sum(component_te(c) for c in placed), "components": placed}
