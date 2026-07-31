"""Simple planning phase allocator for single-pole loads.

This is a load-planning helper, not a substitute for electrical calculation.
"""
PHASES = ("L1", "L2", "L3")


def balance_phases(loads: list[dict]) -> list[dict]:
    totals = {phase: 0.0 for phase in PHASES}
    result = []
    for load in loads:
        name = load.get("name", "Last")
        current = float(load.get("current_a", 0))
        if current < 0:
            raise ValueError("current_a must not be negative")
        phase = min(PHASES, key=lambda p: totals[p])
        totals[phase] += current
        result.append({**load, "phase": phase})
    return {"loads": result, "phase_totals_a": totals}
