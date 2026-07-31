"""Combined circuit, protective device and terminal plan."""
from .terminal_zones import assign_terminal_zones


def build_terminal_plan(circuits: list[dict]) -> list[dict]:
    zones = assign_terminal_zones(circuits)
    outgoing = zones["outgoing"]
    result = []
    for index, circuit in enumerate(circuits):
        phase = circuit.get("phase") or circuit.get("assigned_phases", [None])[0]
        n = f"X4.{index + 1:02d}"
        pe = f"X3.{index + 1:02d}"
        result.append({
            **outgoing[index],
            "protective_device": circuit.get("device"),
            "circuit_number": circuit.get("number", index + 1),
            "phase": phase,
            "fi_group": circuit.get("fi_group"),
            "n_group": circuit.get("n_group"),
            "outgoing_terminal": outgoing[index]["terminal"],
            "n_terminal": n,
            "pe_terminal": pe,
        })
    return result
