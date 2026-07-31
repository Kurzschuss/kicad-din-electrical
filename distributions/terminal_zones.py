"""Separate incoming/feed and outgoing circuit terminal zones."""

ZONE_RAILS = {
    "INCOMING": "X1",
    "OUTGOING": "X2",
    "PE": "X3",
    "N": "X4",
}


def assign_terminal_zones(circuits: list[dict], start_outgoing: int = 1) -> dict:
    if start_outgoing < 1:
        raise ValueError("start_outgoing must be positive")
    outgoing = []
    for index, circuit in enumerate(circuits, start_outgoing):
        outgoing.append({
            **circuit,
            "terminal_zone": "OUTGOING",
            "terminal_rail": ZONE_RAILS["OUTGOING"],
            "terminal": f"{ZONE_RAILS['OUTGOING']}.{index:02d}",
        })
    return {
        "zones": ZONE_RAILS.copy(),
        "incoming": {"zone": "INCOMING", "rail": ZONE_RAILS["INCOMING"]},
        "outgoing": outgoing,
        "pe_rail": ZONE_RAILS["PE"],
        "n_rail": ZONE_RAILS["N"],
    }
