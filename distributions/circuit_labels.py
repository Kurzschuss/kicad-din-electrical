"""Circuit and device labels for the 216-TE distribution plan."""


def label_circuits(circuits: list[dict]) -> list[dict]:
    """Normalize circuit numbers and labels without changing electrical design."""
    result = []
    for index, circuit in enumerate(circuits, 1):
        number = circuit.get("number", index)
        name = str(circuit.get("name", f"Stromkreis {number}")).strip()
        device = circuit.get("device")
        phase = circuit.get("phase")
        fi_group = circuit.get("fi_group")
        result.append({
            **circuit,
            "number": number,
            "label": name,
            "device": device,
            "phase": phase,
            "fi_group": fi_group,
        })
    return result
