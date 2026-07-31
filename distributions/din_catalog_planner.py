"""Add catalog devices to a DIN layout and report remaining capacity."""
from .din_rail_layout import layout_summary
from .unified_din_catalog import unified_catalog


def add_catalog_device(plan: list[dict], device: dict, rails: int = 18, te_per_rail: int = 12) -> dict:
    candidate = list(plan) + [dict(device)]
    summary = layout_summary(candidate, rails=rails, te_per_rail=te_per_rail)
    return summary


def add_by_part_number(plan: list[dict], part_number: str, rails: int = 18, te_per_rail: int = 12) -> dict:
    matches = [d for d in unified_catalog() if str(d.get("part_number")) == str(part_number)]
    if not matches:
        raise KeyError(f"unknown DIN device: {part_number}")
    return add_catalog_device(plan, matches[0], rails=rails, te_per_rail=te_per_rail)
