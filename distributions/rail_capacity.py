"""DIN rail / row capacity model.

The project now treats 12 TE as one planning row. A DIN rail itself is a
mechanical carrier; the 12-TE value is a project planning convention.
"""

TE_PER_ROW = 12
MAX_TE = 216
MAX_ROWS = MAX_TE // TE_PER_ROW


def row_plan(total_te: int, te_per_row: int = TE_PER_ROW) -> list[dict]:
    if not isinstance(total_te, int) or not 0 <= total_te <= MAX_TE:
        raise ValueError(f"total_te must be 0..{MAX_TE}")
    if not isinstance(te_per_row, int) or te_per_row < 1:
        raise ValueError("te_per_row must be positive")
    rows = []
    remaining = total_te
    row = 1
    while remaining and row <= (MAX_TE // te_per_row):
        used = min(remaining, te_per_row)
        rows.append({"row": row, "te_used": used, "reserve_te": te_per_row - used})
        remaining -= used
        row += 1
    if remaining:
        raise ValueError("layout exceeds configured row capacity")
    return rows
