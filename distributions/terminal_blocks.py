"""Terminal-block planning for DIN distribution boards."""

TERMINAL_TYPES = {
    "PE": {"function": "PE", "width_te": 1},
    "N": {"function": "N", "width_te": 1},
    "L1": {"function": "L1", "width_te": 1},
    "L2": {"function": "L2", "width_te": 1},
    "L3": {"function": "L3", "width_te": 1},
    "FEED_THROUGH": {"function": "Durchgang", "width_te": 1},
    "DISCONNECT": {"function": "Trennklemme", "width_te": 1},
    "MEASURE": {"function": "Messklemme", "width_te": 1},
    "MULTI_LEVEL": {"function": "Mehrstock", "width_te": 1},
}


def assign_terminals(circuits: list[dict], start_index: int = 1) -> list[dict]:
    """Create terminal identifiers X1.01, X1.02 ... for circuit connections."""
    if start_index < 1:
        raise ValueError("start_index must be positive")
    result = []
    for offset, circuit in enumerate(circuits):
        terminal_no = start_index + offset
        terminal_type = circuit.get("terminal_type", "FEED_THROUGH")
        if terminal_type not in TERMINAL_TYPES:
            raise ValueError(f"unknown terminal type: {terminal_type}")
        result.append({
            **circuit,
            "terminal": f"X1.{terminal_no:02d}",
            "terminal_type": terminal_type,
            "terminal_function": TERMINAL_TYPES[terminal_type]["function"],
            "terminal_width_te": TERMINAL_TYPES[terminal_type]["width_te"],
            "terminal_rail": circuit.get("terminal_rail", "X1"),
            "terminal_pe": circuit.get("pe_terminal"),
            "terminal_n": circuit.get("n_terminal"),
        })
    return result
