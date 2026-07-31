"""Human-readable L1/L2/L3 planning report."""
from .phase_assignment import assign_group_phases


def report(groups: list[dict]) -> str:
    result = assign_group_phases(groups)
    lines = ["Phasenübersicht", "================"]
    totals = result["phase_totals_a"]
    for phase in ("L1", "L2", "L3"):
        lines.append(f"{phase}: {totals[phase]:.1f} A")
    lines.append("")
    for group in result["groups"]:
        phases = ", ".join(group["assigned_phases"])
        lines.append(f"{group.get('name', 'Gruppe')}: {phases}")
    return "\n".join(lines)
