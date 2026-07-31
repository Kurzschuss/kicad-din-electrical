"""Automatic 216-module field allocation using the device catalog."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES
from .board_layout import FIELD_CAPACITY, MAX_FIELDS


def allocate(devices: list[str], field_capacity: int = FIELD_CAPACITY) -> list[dict]:
    if not devices:
        return []
    widths = []
    for device in devices:
        if device not in DEVICE_WIDTHS:
            raise ValueError(f"unknown device type: {device}")
        widths.append(DEVICE_WIDTHS[device])
    total = sum(widths)
    if total > MAX_MODULES:
        raise ValueError(f"{total} modules requested; maximum is {MAX_MODULES}")
    if field_capacity < 1 or field_capacity > FIELD_CAPACITY:
        raise ValueError("field_capacity must be 1..36")

    fields = []
    current = []
    used = 0
    for device, width in zip(devices, widths):
        if width > field_capacity:
            raise ValueError(f"{device} is wider than the field capacity")
        if used + width > field_capacity:
            fields.append({"field": len(fields) + 1, "devices": current, "modules": used, "reserve": field_capacity - used})
            current, used = [], 0
        current.append(device)
        used += width
    if current:
        fields.append({"field": len(fields) + 1, "devices": current, "modules": used, "reserve": field_capacity - used})
    if len(fields) > MAX_FIELDS:
        raise ValueError("allocation requires more than 6 fields / 216 modules")
    return fields
