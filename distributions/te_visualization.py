"""Render the canonical 18 x 12 TE layout."""
from .te_rows import TE_PER_ROW, MAX_ROWS, assign_te_rows


def render(devices: list[str]) -> str:
    placements = assign_te_rows(devices)
    rows = [[] for _ in range(MAX_ROWS)]
    for p in placements:
        rows[p["row"] - 1].append(p)
    lines = []
    for index, row in enumerate(rows, 1):
        first = (index - 1) * TE_PER_ROW + 1
        last = index * TE_PER_ROW
        entries = " | ".join(f"{p['device']} [{p['start_te']}-{p['end_te']}]" for p in row)
        if not entries:
            entries = "RESERVE"
        lines.append(f"Reihe {index:02d}  TE {first:03d}-{last:03d}: {entries}")
    return "\n".join(lines)
