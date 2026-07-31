"""Detailed six-field plan for DIN distribution boards."""
from .auto_distribution import allocate

FIELD_CAPACITY = 36
MAX_FIELDS = 6
MAX_MODULES = FIELD_CAPACITY * MAX_FIELDS


def detailed_plan(devices: list[str]) -> dict:
    fields = allocate(devices, FIELD_CAPACITY)
    return {
        "max_modules": MAX_MODULES,
        "field_capacity": FIELD_CAPACITY,
        "field_count": len(fields),
        "total_modules": sum(f["modules"] for f in fields),
        "fields": fields,
    }
