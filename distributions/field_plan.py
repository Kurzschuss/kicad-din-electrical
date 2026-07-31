"""Detailed 18-row plan for DIN distribution boards."""
from .auto_distribution import allocate
from .board_layout import TE_PER_ROW, MAX_ROWS, MAX_MODULES

FIELD_CAPACITY = TE_PER_ROW
MAX_FIELDS = MAX_ROWS


def detailed_plan(devices: list[str]) -> dict:
    rows = allocate(devices, TE_PER_ROW)
    return {
        "max_modules": MAX_MODULES,
        "max_te": MAX_MODULES,
        "row_capacity_te": TE_PER_ROW,
        "field_capacity": TE_PER_ROW,
        "row_count": len(rows),
        "field_count": len(rows),
        "total_modules": sum(r["modules"] for r in rows),
        "total_te": sum(r["te_used"] for r in rows),
        "rows": rows,
        "fields": rows,
    }
