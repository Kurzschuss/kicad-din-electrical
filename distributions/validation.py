"""Validation helpers for large DIN distribution layouts."""
from .device_catalog import DEVICE_WIDTHS, MAX_MODULES
from .auto_distribution import allocate

MAX_FIELDS = 6
FIELD_CAPACITY = 36


def validate_devices(devices: list[str]) -> dict:
    unknown = [d for d in devices if d not in DEVICE_WIDTHS]
    if unknown:
        raise ValueError("unknown device types: " + ", ".join(unknown))
    total = sum(DEVICE_WIDTHS[d] for d in devices)
    if total > MAX_MODULES:
        raise ValueError(f"layout requires {total} modules; maximum is {MAX_MODULES}")
    fields = allocate(devices)
    warnings = []
    if len(fields) == MAX_FIELDS and fields[-1]["reserve"] == 0:
        warnings.append("216 modules fully allocated; no module reserve remains")
    if any(f["reserve"] < 2 for f in fields):
        warnings.append("one or more fields have less than 2 reserve modules")
    return {"valid": True, "modules": total, "fields": len(fields), "warnings": warnings}
