"""Selection helpers for building a DIN plan from the unified catalog."""
from .din_catalog_planner import add_catalog_device
from .unified_din_catalog import search_devices


def select_and_add(plan: list[dict], query: str, index: int = 0, rails: int = 18, te_per_rail: int = 12) -> dict:
    matches = search_devices(query)
    if not matches:
        raise KeyError(f"no DIN device matches: {query}")
    if index < 0 or index >= len(matches):
        raise IndexError("catalog selection index out of range")
    return add_catalog_device(plan, matches[index], rails=rails, te_per_rail=te_per_rail)


def remaining_te(plan: list[dict], rails: int = 18, te_per_rail: int = 12) -> int:
    return add_catalog_device([], {}, rails=rails, te_per_rail=te_per_rail)["capacity_te"] - sum(int(c.get("width_te", 1)) for c in plan)
