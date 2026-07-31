"""Define deterministic logical pins for DIN components and terminals."""


def _pins(*names: str) -> list[dict]:
    return [{"number": str(i + 1), "name": name} for i, name in enumerate(names)]


def pins_for_component(component: dict) -> list[dict]:
    kind = component.get("component_type")
    poles = int(component.get("poles", 0) or 0)
    voltage = component.get("output_voltage")

    if kind == "DIN_RAIL_POWER_SUPPLY":
        if int(voltage or 0) in (5, 12, 24):
            return _pins("L", "N", "PE", f"+{int(voltage)}V", "0V")
        return _pins("L", "N", "PE", "OUT+", "OUT-")

    if kind == "DIN_RAIL_MAIN_SWITCH":
        names = [f"L{i}" for i in range(1, poles + 1)]
        return _pins(*names, *[f"T{i}" for i in range(1, poles + 1)])

    if kind == "DIN_RAIL_TRANSFER_SWITCH":
        return _pins(*[f"COM{i}" for i in range(1, poles + 1)], *[f"A{i}" for i in range(1, poles + 1)], *[f"B{i}" for i in range(1, poles + 1)])

    if kind == "DIN_RAIL_SURGE_PROTECTION":
        return _pins(*[f"L{i}" for i in range(1, poles + 1)], "PE")

    if kind == "DIN_RAIL_TERMINAL_BLOCK":
        count = int(component.get("connection_count", 2))
        return _pins(*[f"CONN{i}" for i in range(1, count + 1)])

    return []


def build_pin_manifest(components: list[dict], terminals: list[dict]) -> list[dict]:
    result = []
    for component in components:
        result.append({"reference": component.get("reference"), "pins": pins_for_component(component)})
    for terminal in terminals:
        result.append({"reference": terminal.get("reference"), "pins": pins_for_component({**terminal, "component_type": "DIN_RAIL_TERMINAL_BLOCK"})})
    return result
