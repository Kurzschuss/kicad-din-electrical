"""Catalog-to-editor helpers for adding DIN devices to the layout."""
from .din_device_catalog import load_catalog
from .din_rail_auto_place import find_free_position


def catalog_choices(path=None) -> list[dict]:
    catalog = load_catalog(path) if path else load_catalog()
    return [dict(item) for item in catalog]


def add_catalog_device(components: list[dict], device: dict, rails: int = 18, te_per_rail: int = 12) -> list[dict]:
    reference = str(device.get("reference") or "")
    if not reference:
        raise ValueError("device reference is required")
    if any(str(c.get("reference")) == reference for c in components):
        raise ValueError(f"reference already exists: {reference}")
    width = int(device.get("width_te", device.get("te", 1)))
    rail, start = find_free_position(components, width, rails, te_per_rail)
    item = dict(device)
    item.update({"rail": rail, "start_te": start, "end_te": start + width - 1, "width_te": width})
    return [*components, item]
