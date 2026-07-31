"""Find free DIN-rail positions and safely move components."""
from .din_rail_layout import component_te, validate_rail_layout


def find_free_position(components: list[dict], width_te: int, rails: int = 18, te_per_rail: int = 12) -> tuple[int, int]:
    width_te = int(width_te)
    if width_te < 1 or width_te > int(te_per_rail):
        raise ValueError("invalid component width")
    occupied = {}
    for item in components:
        rail = int(item.get("rail", 1))
        start = int(item.get("start_te", 1))
        end = int(item.get("end_te", start + component_te(item) - 1))
        occupied.setdefault(rail, []).append((start, end))
    for rail in range(1, int(rails) + 1):
        ranges = sorted(occupied.get(rail, []))
        candidate = 1
        for start, end in ranges:
            if candidate + width_te - 1 < start:
                return rail, candidate
            candidate = max(candidate, end + 1)
        if candidate + width_te - 1 <= int(te_per_rail):
            return rail, candidate
    raise ValueError("no free DIN rail position available")


def auto_place_component(components: list[dict], reference: str, rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    target = next((c for c in components if str(c.get("reference")) == str(reference)), None)
    if target is None:
        raise KeyError(f"unknown component reference: {reference}")
    others = [dict(c) for c in components if str(c.get("reference")) != str(reference)]
    rail, start = find_free_position(others, component_te(target), rails, te_per_rail)
    moved = dict(target)
    moved.update({"rail": rail, "start_te": start, "end_te": start + component_te(target) - 1})
    result = others + [moved]
    errors = validate_rail_layout(result)
    if errors:
        raise ValueError("auto-placement produced an invalid layout: " + "; ".join(errors))
    return result
