"""Canonical 216-TE distribution board layout: 18 rows x 12 TE."""

MAX_MODULES = 216
TE_PER_ROW = 12
MAX_ROWS = 18
FIELD_CAPACITY = TE_PER_ROW  # compatibility alias
MAX_FIELDS = MAX_ROWS  # compatibility alias


def layout(total_modules: int, field_capacity: int = TE_PER_ROW) -> list[dict]:
    if not isinstance(total_modules, int) or not 0 <= total_modules <= MAX_MODULES:
        raise ValueError(f"total_modules must be 0..{MAX_MODULES}")
    if not isinstance(field_capacity, int) or not 1 <= field_capacity <= TE_PER_ROW:
        raise ValueError(f"field_capacity must be 1..{TE_PER_ROW}")

    rows = []
    remaining = total_modules
    for row_no in range(1, MAX_ROWS + 1):
        used = min(remaining, field_capacity)
        rows.append({"row": row_no, "field": row_no, "modules": used, "te_used": used, "reserve": field_capacity - used, "reserve_te": field_capacity - used})
        remaining -= used
    return rows


PRESETS = {n: layout(n) for n in (12, 24, 36, 48, 60, 72, 108, 144, 180, 216)}
