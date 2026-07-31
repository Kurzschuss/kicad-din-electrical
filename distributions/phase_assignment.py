"""Phase assignment metadata for distribution groups."""
PHASES = ("L1", "L2", "L3")


def assign_group_phases(groups: list[dict]) -> list[dict]:
    """Assign single-phase groups to the least-loaded phase.

    Existing explicit phases are retained. Three-/four-pole groups are marked
    as all-phase consumers. This is only a planning aid, not a load calculation.
    """
    totals = {phase: 0.0 for phase in PHASES}
    result = []
    for group in groups:
        width = int(group.get("phase_poles", 1))
        current = float(group.get("current_a", 0))
        if current < 0:
            raise ValueError("current_a must not be negative")
        explicit = group.get("phase")
        if width >= 3:
            phases = list(PHASES)
            for phase in phases:
                totals[phase] += current
        elif explicit in PHASES:
            phases = [explicit]
            totals[explicit] += current
        else:
            phase = min(PHASES, key=lambda p: totals[p])
            phases = [phase]
            totals[phase] += current
        result.append({**group, "assigned_phases": phases})
    return {"groups": result, "phase_totals_a": totals}
