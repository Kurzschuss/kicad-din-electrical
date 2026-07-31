"""Configurable terminal naming schema and presets."""

SCHEMAS = {
    "IEC": {"rail_prefix": "X", "separator": ".", "number_width": 2},
    "COMPACT": {"rail_prefix": "X", "separator": "", "number_width": 2},
    "LABEL": {"rail_prefix": "", "separator": "-", "number_width": 2},
}


def get_schema(name: str = "IEC") -> dict:
    key = str(name).upper()
    if key not in SCHEMAS:
        raise ValueError(f"unknown terminal schema: {name}")
    return dict(SCHEMAS[key])


def merge_schema(name: str = "IEC", **overrides) -> dict:
    schema = get_schema(name)
    schema.update({k: v for k, v in overrides.items() if v is not None})
    return schema
