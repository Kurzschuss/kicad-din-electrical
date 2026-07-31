"""Electrical group planning for DIN distribution boards.

This models logical grouping only; it does not certify a wiring design.
"""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES


def build_groups(groups: list[dict]) -> dict:
    total = 0
    result = []
    for index, group in enumerate(groups, 1):
        name = group.get("name", f"Gruppe {index}")
        protective = group.get("protective_device")
        devices = group.get("devices", [])
        if protective and protective not in DEVICE_WIDTHS:
            raise ValueError(f"unknown protective device: {protective}")
        for device in devices:
            if device not in DEVICE_WIDTHS:
                raise ValueError(f"unknown device type: {device}")
        width = (DEVICE_WIDTHS.get(protective, 0) +
                 sum(DEVICE_WIDTHS[d] for d in devices))
        total += width
        result.append({
            "group": name,
            "protective_device": protective,
            "devices": devices,
            "modules": width,
            "neutral_group": group.get("neutral_group"),
            "phase": group.get("phase"),
            "busbar": group.get("busbar"),
        })
    if total > MAX_MODULES:
        raise ValueError(f"groups require {total} modules; maximum is {MAX_MODULES}")
    return {"modules": total, "groups": result}
