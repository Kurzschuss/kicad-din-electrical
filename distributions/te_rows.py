"""Canonical 18-row x 12-TE distribution layout."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES

TE_PER_ROW = 12
MAX_ROWS = 18
MAX_TE = TE_PER_ROW * MAX_ROWS


def assign_te_rows(devices: list[str]) -> list[dict]:
    if sum(DEVICE_WIDTHS.get(d, 0) for d in devices) > MAX_TE:
        raise ValueError(f"layout exceeds {MAX_TE} TE")
    rows = []
    row = 1
    offset = 0
    for device in devices:
        if device not in DEVICE_WIDTHS:
            raise ValueError(f"unknown device type: {device}")
        width = DEVICE_WIDTHS[device]
        if width > TE_PER_ROW:
            raise ValueError(f"{device} exceeds one {TE_PER_ROW}-TE row")
        if offset + width > TE_PER_ROW:
            row += 1
            offset = 0
        if row > MAX_ROWS:
            raise ValueError(f"layout exceeds {MAX_ROWS} rows / {MAX_TE} TE")
        start = (row - 1) * TE_PER_ROW + offset + 1
        end = start + width - 1
        rows.append({"row": row, "device": device, "start_te": start, "end_te": end, "width_te": width})
        offset += width
    return rows
