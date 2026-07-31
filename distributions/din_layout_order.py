"""Reorder DIN components and re-pack them without changing terminal labels."""
from .din_rail_layout import layout_components


def reorder_components(components: list[dict], order: list[int], rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    if sorted(order) != list(range(len(components))):
        raise ValueError("order must contain each component index exactly once")
    reordered = [dict(components[i]) for i in order]
    return layout_components(reordered, rails=rails, te_per_rail=te_per_rail)


def sort_components(components: list[dict], key: str = "rail", reverse: bool = False, rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    ordered = sorted((dict(c) for c in components), key=lambda c: c.get(key, ""), reverse=reverse)
    return layout_components(ordered, rails=rails, te_per_rail=te_per_rail)
