"""DIN distribution module planner.

Supports up to 216 DIN modules and splits a board into rows/fields while
preserving the requested device widths. This is a planning helper; final
installation dimensions and device compatibility must be verified separately.
"""

MAX_MODULES = 216
DEFAULT_ROW_CAPACITY = 36


def validate_total_modules(total_modules: int) -> None:
    if not isinstance(total_modules, int):
        raise TypeError("total_modules must be an integer")
    if total_modules < 1 or total_modules > MAX_MODULES:
        raise ValueError(f"total_modules must be between 1 and {MAX_MODULES}")


def plan_rows(total_modules: int, row_capacity: int = DEFAULT_ROW_CAPACITY) -> list[int]:
    validate_total_modules(total_modules)
    if not isinstance(row_capacity, int) or row_capacity < 1:
        raise ValueError("row_capacity must be a positive integer")
    if row_capacity > MAX_MODULES:
        raise ValueError(f"row_capacity must not exceed {MAX_MODULES}")

    rows = []
    remaining = total_modules
    while remaining:
        used = min(remaining, row_capacity)
        rows.append(used)
        remaining -= used
    return rows


def place_devices(widths: list[int], row_capacity: int = DEFAULT_ROW_CAPACITY) -> list[list[int]]:
    """Pack device widths into rows without exceeding row_capacity."""
    if any(not isinstance(width, int) or width < 1 for width in widths):
        raise ValueError("device widths must be positive integers")
    total = sum(widths)
    validate_total_modules(total)
    rows: list[list[int]] = [[]]
    used = 0
    for width in widths:
        if used + width > row_capacity:
            rows.append([])
            used = 0
        if width > row_capacity:
            raise ValueError("a device is wider than the row capacity")
        rows[-1].append(width)
        used += width
    return rows


if __name__ == "__main__":
    for total in (108, 144, 180, 216):
        rows = plan_rows(total)
        print(f"{total} modules -> {len(rows)} rows: {rows}")
