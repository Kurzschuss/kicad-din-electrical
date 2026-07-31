"""Map each circuit to PE/N/phase terminals on terminal rail X1."""

PHASE_TERMINAL_TYPES = {"L1", "L2", "L3"}


def map_terminals(circuits: list[dict], start_index: int = 1) -> list[dict]:
    if start_index < 1:
        raise ValueError("start_index must be positive")
    result = []
    next_no = start_index
    for circuit in circuits:
        phase = circuit.get("phase")
        if phase not in PHASE_TERMINAL_TYPES:
            phase = circuit.get("assigned_phases", [None])[0]
        terminals = {"phase": None, "n": None, "pe": None}
        if phase in PHASE_TERMINAL_TYPES:
            terminals["phase"] = f"X1.{next_no:02d}"
            next_no += 1
        terminals["n"] = f"X1.{next_no:02d}"
        next_no += 1
        terminals["pe"] = f"X1.{next_no:02d}"
        next_no += 1
        result.append({**circuit, "terminals": terminals, "terminal_rail": "X1"})
    return result
