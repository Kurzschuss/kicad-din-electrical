"""216-module distribution board layout presets."""

MAX_MODULES = 216
FIELD_CAPACITY = 36
MAX_FIELDS = 6


def layout(total_modules: int, field_capacity: int = FIELD_CAPACITY) -> list[dict]:
    if not isinstance(total_modules, int) or not 1 <= total_modules <= MAX_MODULES:
        raise ValueError(f"total_modules must be 1..{MAX_MODULES}")
    if not isinstance(field_capacity, int) or not 1 <= field_capacity <= FIELD_CAPACITY:
        raise ValueError("field_capacity must be 1..36")

    fields = []
    remaining = total_modules
    for field_no in range(1, MAX_FIELDS + 1):
        if remaining <= 0:
            break
        used = min(remaining, field_capacity)
        fields.append({"field": field_no, "modules": used, "reserve": field_capacity - used})
        remaining -= used
    return fields


PRESETS = {n: layout(n) for n in (36, 72, 108, 144, 180, 216)}
