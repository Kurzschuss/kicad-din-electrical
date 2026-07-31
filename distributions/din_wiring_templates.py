"""Generate common wiring templates for DIN devices and terminal blocks."""
from .din_pin_mapping import pins_for_component


def wire_device_to_terminals(device: dict, terminal_refs: list[str], nets: list[str]) -> list[dict]:
    """Create deterministic device-pin -> terminal-pin connections.

    The caller controls terminal references and net names; no physical pin
    numbers are guessed beyond the logical pin manifest.
    """
    pins = pins_for_component(device)
    if len(terminal_refs) != len(nets):
        raise ValueError("terminal_refs and nets must have the same length")
    if len(terminal_refs) > len(pins):
        raise ValueError("not enough logical device pins for requested wiring")

    result = []
    for index, (terminal_ref, net) in enumerate(zip(terminal_refs, nets)):
        result.append({
            "source_ref": device.get("reference"),
            "source_pin": pins[index]["number"],
            "source_pin_name": pins[index]["name"],
            "target_ref": terminal_ref,
            "target_pin": "1",
            "net": net,
        })
    return result


def transfer_switch_nets(device: dict, terminal_refs: list[str], pole_count: int) -> list[dict]:
    """Template the three contacts per pole of a 2P/3P/4P transfer switch."""
    if pole_count not in (2, 3, 4):
        raise ValueError("pole_count must be 2, 3 or 4")
    expected = pole_count * 3
    if len(terminal_refs) != expected:
        raise ValueError(f"expected {expected} terminal references")

    connections = []
    for pole in range(1, pole_count + 1):
        for contact, offset in (("COM", 0), ("A", pole_count), ("B", pole_count * 2)):
            index = offset + pole - 1
            connections.append({
                "source_ref": device.get("reference"),
                "source_pin": f"{contact}{pole}",
                "target_ref": terminal_refs[index],
                "target_pin": "1",
                "net": f"{contact}{pole}",
            })
    return connections
