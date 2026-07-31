"""Place DIN-rail components using TE width and validate rail capacity."""

MAX_TE_PER_RAIL = 12
DEFAULT_RAILS = 18


def component_te(component: dict) -> int:
    return int(component.get("width_te", component.get("te", 1)))


def layout_components(components: list[dict], rails: int = DEFAULT_RAILS, te_per_rail: int = MAX_TE_PER_RAIL) -> list[dict]:
    rails = int(rails); te_per_rail = int(te_per_rail)
    if rails < 1 or te_per_rail < 1:
        raise ValueError("rails and te_per_rail must be positive")
    result = []
    rail = 1
    used = 0
    for index, component in enumerate(components, 1):
        width = component_te(component)
        if width < 1:
            raise ValueError(f"component {index} has invalid TE width")
        if width > te_per_rail:
            raise ValueError(f"component {index} is wider than one DIN rail")
        if used + width > te_per_rail:
            rail += 1
            used = 0
        if rail > rails:
            raise ValueError("DIN rail capacity exceeded")
        item = dict(component)
        item.update({"rail": rail, "start_te": used + 1, "end_te": used + width, "width_te": width})
        result.append(item)
        used += width
    return result


def total_te(components: list[dict]) -> int:
    return sum(component_te(component) for component in components)


def layout_summary(components: list[dict], rails: int = DEFAULT_RAILS, te_per_rail: int = MAX_TE_PER_RAIL) -> dict:
    placed = layout_components(components, rails, te_per_rail)
    used_by_rail = {rail: 0 for rail in range(1, int(rails) + 1)}
    for item in placed:
        used_by_rail[item["rail"]] += item["width_te"]
    used = sum(used_by_rail.values())
    capacity = int(rails) * int(te_per_rail)
    return {"components": placed, "rails": int(rails), "te_per_rail": int(te_per_rail), "capacity_te": capacity, "used_te": used, "free_te": capacity - used, "used_by_rail": used_by_rail}
