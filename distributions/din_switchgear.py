"""DIN-rail mains transfer switches, main switches and surge protection."""

POLES = (2, 3, 4)


def transfer_switch(poles: int, width_te: int, **metadata) -> dict:
    poles = int(poles); width_te = int(width_te)
    if poles not in POLES:
        raise ValueError("poles must be 2, 3 or 4")
    if width_te < poles:
        raise ValueError("width_te must accommodate the selected poles")
    return {
        "component_type": "DIN_RAIL_TRANSFER_SWITCH",
        "poles": poles,
        "changeover_contact": True,
        "width_te": width_te,
        "din_rail": True,
        **metadata,
    }


def main_switch(poles: int, width_te: int, **metadata) -> dict:
    poles = int(poles); width_te = int(width_te)
    if poles not in POLES:
        raise ValueError("poles must be 2, 3 or 4")
    if width_te < poles:
        raise ValueError("width_te must accommodate the selected poles")
    return {
        "component_type": "DIN_RAIL_MAIN_SWITCH",
        "poles": poles,
        "width_te": width_te,
        "din_rail": True,
        **metadata,
    }


def surge_protection(type_name: str = "SPD", poles: int = 4, width_te: int = 4, **metadata) -> dict:
    if poles not in POLES:
        raise ValueError("poles must be 2, 3 or 4")
    if width_te < 1:
        raise ValueError("width_te must be positive")
    return {
        "component_type": "DIN_RAIL_SURGE_PROTECTION",
        "type": type_name,
        "poles": poles,
        "width_te": width_te,
        "din_rail": True,
        **metadata,
    }


def switchgear_options() -> list[dict]:
    result = []
    for poles in POLES:
        result.append(transfer_switch(poles, poles))
        result.append(main_switch(poles, poles))
    result.append(surge_protection())
    return result
