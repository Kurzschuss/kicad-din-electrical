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


def validate_rail_layout(components: list[dict]) -> list[str]:
    errors = []
    by_rail: dict[str, list[tuple[int, int, str]]] = {}
    for item in components:
        rail = str(item.get("rail", 1))
        start = int(item.get("start_te", 1))
        end = int(item.get("end_te", start + component_te(item) - 1))
        if start < 1 or end < start:
            errors.append(f"{item.get('reference', '?')}: invalid TE range {start}-{end}")
            continue
        by_rail.setdefault(rail, []).append((start, end, str(item.get("reference", "?"))))
    for rail, ranges in by_rail.items():
        ranges.sort()
        for previous, current in zip(ranges, ranges[1:]):
            if current[0] <= previous[1]:
                errors.append(f"rail {rail}: TE overlap {previous[2]} ({previous[0]}-{previous[1]}) / {current[2]} ({current[0]}-{current[1]})")
    return errors


def total_te(components: list[dict]) -> int:
    return sum(component_te(component) for component in components)


def layout_summary(components: list[dict], rails: int = DEFAULT_RAILS, te_per_rail: int = MAX_TE_PER_RAIL) -> dict:
    placed = layout_components(components, rails, te_per_rail)
    used_by_rail = {rail: 0 for rail in range(1, int(rails) + 1)}
    for item in placed:
        used_by_rail[item["rail"]] += item["width_te"]
    used = sum(used_by_rail.values())
    capacity = int(rails) * int(te_per_rail)
    return {"components": placed, "rails": int(rails), "te_per_rail": int(te_per_rail), "capacity_te": capacity, "used_te": used, "free_te": capacity - used, "used_by_rail": used_by_rail, "errors": validate_rail_layout(placed)}
