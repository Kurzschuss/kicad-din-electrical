"""DIN-rail terminal block catalog with editable labels and TE footprint."""


def terminal_block(part_number: str, manufacturer: str, width_te: int = 1, connection_count: int = 2, **spec) -> dict:
    width_te = int(width_te)
    connection_count = int(connection_count)
    if width_te < 1:
        raise ValueError("width_te must be positive")
    if connection_count < 1:
        raise ValueError("connection_count must be positive")
    return {
        "component_type": "DIN_RAIL_TERMINAL_BLOCK",
        "part_number": part_number,
        "manufacturer": manufacturer,
        "width_te": width_te,
        "connection_count": connection_count,
        "din_rail": True,
        "terminal_label_policy": "MANUAL",
        "can_edit_label": True,
        **spec,
    }


def generic_terminal_catalog() -> list[dict]:
    return [
        terminal_block("TB-PE", "GENERIC", terminal_function="PE"),
        terminal_block("TB-N", "GENERIC", terminal_function="N"),
        terminal_block("TB-L", "GENERIC", terminal_function="L"),
        terminal_block("TB-DC+", "GENERIC", terminal_function="+24V"),
        terminal_block("TB-DC-", "GENERIC", terminal_function="0V"),
    ]
