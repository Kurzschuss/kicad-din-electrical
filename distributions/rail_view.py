"""Render exact 1..216 DIN positions with multi-module device blocks."""
from .positions import assign_positions

FIELD_CAPACITY = 36
MAX_FIELDS = 6


def render(devices: list[str]) -> str:
    placements = assign_positions(devices)
    fields = {n: ["RESERVE"] * FIELD_CAPACITY for n in range(1, MAX_FIELDS + 1)}
    for p in placements:
        for pos in range(p["start"], p["end"] + 1):
            local = pos - (p["field"] - 1) * FIELD_CAPACITY - 1
            fields[p["field"]][local] = p["device"]

    lines = []
    for field_no, slots in fields.items():
        first = (field_no - 1) * FIELD_CAPACITY + 1
        last = field_no * FIELD_CAPACITY
        lines.append(f"Feld {field_no}: Module {first:03d}-{last:03d}")
        lines.append(" | " + " | ".join(slots) + " |")
    return "\n".join(lines)
