"""DIN-rail power supplies and DC converters for 5 V, 12 V and 24 V."""

OUTPUT_VOLTAGES = (5, 12, 24)
DEFAULT_WIDTHS_TE = (1, 2, 3, 4)


def power_supply(output_voltage: int, width_te: int, output_current_a: float | None = None,
                 power_w: float | None = None, **metadata) -> dict:
    voltage = int(output_voltage)
    width = int(width_te)
    if voltage not in OUTPUT_VOLTAGES:
        raise ValueError("output_voltage must be 5, 12 or 24 V")
    if width < 1:
        raise ValueError("width_te must be positive")
    if output_current_a is not None and output_current_a <= 0:
        raise ValueError("output_current_a must be positive")
    if power_w is not None and power_w <= 0:
        raise ValueError("power_w must be positive")
    return {
        "component_type": "DIN_RAIL_POWER_SUPPLY",
        "input_voltage": metadata.pop("input_voltage", "230VAC"),
        "output_voltage": voltage,
        "output_current_a": output_current_a,
        "power_w": power_w,
        "width_te": width,
        "din_rail": True,
        **metadata,
    }


def power_supply_options() -> list[dict]:
    return [power_supply(v, w) for v in OUTPUT_VOLTAGES for w in DEFAULT_WIDTHS_TE]
