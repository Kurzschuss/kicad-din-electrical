"""Assign absolute DIN module positions (1..216) to devices."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES

FIELD_CAPACITY = 36
MAX_FIELDS = 6


def assign_positions(devices: list[str], field_capacity: int = FIELD_CAPACITY) -> list[dict]:
    if not 1 <= field_capacity <= FIELD_CAPACITY:
        raise ValueError("field_capacity must be 1..36")
    positions = []
    field = 1
    offset = 0
    for device in devices:
        if device not in DEVICE_WIDTHS:
            raise ValueError(f"unknown device type: {device}")
        width = DEVICE_WIDTHS[device]
        if width > field_capacity:
            raise ValueError(f"{device} exceeds field capacity")
        if offset + width > field_capacity:
            field += 1
            offset = 0
        if field > MAX_FIELDS:
            raise ValueError(f"layout exceeds {MAX_MODULES} modules")
        start = (field - 1) * field_capacity + offset + 1
        end = start + width - 1
        positions.append({"device": device, "field": field, "start": start, "end": end, "width": width})
        offset += width
    return positions
