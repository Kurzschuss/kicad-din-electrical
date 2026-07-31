"""Assign absolute DIN positions 1..216 TE to devices in 12-TE rows."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES

TE_PER_ROW = 12
MAX_ROWS = 18
FIELD_CAPACITY = TE_PER_ROW  # compatibility alias
MAX_FIELDS = MAX_ROWS  # compatibility alias


def assign_positions(devices: list[str], field_capacity: int = TE_PER_ROW) -> list[dict]:
    if not 1 <= field_capacity <= TE_PER_ROW:
        raise ValueError(f"field_capacity must be 1..{TE_PER_ROW}")
    positions = []
    row = 1
    offset = 0
    for device in devices:
        if device not in DEVICE_WIDTHS:
            raise ValueError(f"unknown device type: {device}")
        width = DEVICE_WIDTHS[device]
        if width > field_capacity:
            raise ValueError(f"{device} exceeds row capacity")
        if offset + width > field_capacity:
            row += 1
            offset = 0
        if row > MAX_ROWS:
            raise ValueError(f"layout exceeds {MAX_MODULES} TE / {MAX_ROWS} rows")
        start = (row - 1) * field_capacity + offset + 1
        end = start + width - 1
        positions.append({"device": device, "row": row, "field": row, "start": start, "end": end, "start_te": start, "end_te": end, "width": width, "width_te": width})
        offset += width
    return positions
