"""Combine circuit labels with exact 1..216 TE positions."""
from .positions import assign_positions
from .circuit_labels import label_circuits


def assign_circuit_positions(circuits: list[dict]) -> list[dict]:
    labeled = label_circuits(circuits)
    devices = [c["device"] for c in labeled]
    placements = assign_positions(devices)
    result = []
    for circuit, placement in zip(labeled, placements):
        result.append({**circuit, **placement})
    return result
