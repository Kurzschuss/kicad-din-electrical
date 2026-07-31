"""Automatic 216-TE row allocation using the device catalog."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES
from .board_layout import TE_PER_ROW, MAX_ROWS

FIELD_CAPACITY = TE_PER_ROW  # compatibility alias
MAX_FIELDS = MAX_ROWS  # compatibility alias


def allocate(devices: list[str], field_capacity: int = TE_PER_ROW) -> list[dict]:
    if not devices:
        return []
    widths = []
    for device in devices:
        if device not in DEVICE_WIDTHS:
            raise ValueError(f"unknown device type: {device}")
        widths.append(DEVICE_WIDTHS[device])
    total = sum(widths)
    if total > MAX_MODULES:
        raise ValueError(f"{total} TE requested; maximum is {MAX_MODULES} TE")
    if field_capacity < 1 or field_capacity > TE_PER_ROW:
        raise ValueError(f"field_capacity must be 1..{TE_PER_ROW}")

    rows = []
    current = []
    used = 0
    for device, width in zip(devices, widths):
        if width > field_capacity:
            raise ValueError(f"{device} is wider than the row capacity")
        if used + width > field_capacity:
            rows.append({"row": len(rows) + 1, "field": len(rows) + 1, "devices": current, "modules": used, "te_used": used, "reserve": field_capacity - used, "reserve_te": field_capacity - used})
            current, used = [], 0
        current.append(device)
        used += width
    if current:
        rows.append({"row": len(rows) + 1, "field": len(rows) + 1, "devices": current, "modules": used, "te_used": used, "reserve": field_capacity - used, "reserve_te": field_capacity - used})
    if len(rows) > MAX_ROWS:
        raise ValueError(f"allocation requires more than {MAX_ROWS} rows / {MAX_MODULES} TE")
    return rows
