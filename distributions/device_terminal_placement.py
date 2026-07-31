"""Associate terminal blocks with their source DIN devices and place them nearby."""
from .din_rail_layout import component_te


def place_terminals_near_devices(devices: list[dict], terminals: list[dict], max_distance_te: int = 12) -> list[dict]:
    """Assign each terminal to its referenced device and suggest a nearby position."""
    by_id = {d.get("id"): d for d in devices if d.get("id") is not None}
    result = []
    for terminal in terminals:
        item = dict(terminal)
        device = by_id.get(terminal.get("device_id"))
        if device is not None:
            item["source_device_id"] = device.get("id")
            item["source_device"] = device.get("part_number") or device.get("component_type")
            item["preferred_rail"] = device.get("rail")
            start = int(device.get("start_te", 1))
            width = component_te(device)
            item["preferred_te"] = min(start + width, start + max_distance_te)
        result.append(item)
    return result
