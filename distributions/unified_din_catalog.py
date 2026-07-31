"""Unified catalog for all DIN-rail components used by the planner."""
from .din_device_catalog import generic_catalog
from .terminal_catalog import generic_terminal_catalog


def unified_catalog() -> list[dict]:
    return generic_catalog() + generic_terminal_catalog()


def catalog_by_type() -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for item in unified_catalog():
        result.setdefault(item["component_type"], []).append(item)
    return result


def find_devices(component_type: str | None = None, output_voltage: int | None = None, poles: int | None = None) -> list[dict]:
    items = unified_catalog()
    if component_type is not None:
        items = [item for item in items if item.get("component_type") == component_type]
    if output_voltage is not None:
        items = [item for item in items if item.get("output_voltage") == int(output_voltage)]
    if poles is not None:
        items = [item for item in items if item.get("poles") == int(poles)]
    return items


def search_devices(query: str) -> list[dict]:
    q = str(query).strip().lower()
    if not q:
        return unified_catalog()
    return [item for item in unified_catalog() if q in " ".join(str(v) for v in item.values()).lower()]
