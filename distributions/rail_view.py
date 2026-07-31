"""Render exact 1..216 TE DIN positions with multi-module device blocks."""
from .positions import assign_positions

TE_PER_ROW = 12
MAX_ROWS = 18
FIELD_CAPACITY = TE_PER_ROW
MAX_FIELDS = MAX_ROWS


def render(devices: list[str]) -> str:
    placements = assign_positions(devices)
    rows = {n: ["RESERVE"] * TE_PER_ROW for n in range(1, MAX_ROWS + 1)}
    for p in placements:
        for pos in range(p["start"], p["end"] + 1):
            local = pos - (p["row"] - 1) * TE_PER_ROW - 1
            rows[p["row"]][local] = p["device"]

    lines = []
    for row_no, slots in rows.items():
        first = (row_no - 1) * TE_PER_ROW + 1
        last = row_no * TE_PER_ROW
        lines.append(f"Reihe {row_no:02d}: TE {first:03d}-{last:03d}")
        lines.append(" | " + " | ".join(slots) + " |")
    return "\n".join(lines)
