"""Combined planning model for a DIN distribution up to 216 modules."""
from .positions import assign_positions
from .groups import build_groups
from .group_validation import validate_groups
from .phase_assignment import assign_group_phases


def build_distribution(devices: list[str], groups: list[dict] | None = None) -> dict:
    groups = groups or []
    positions = assign_positions(devices)
    group_model = build_groups(groups)
    warnings = validate_groups(groups)
    phases = assign_group_phases(groups) if groups else {"groups": [], "phase_totals_a": {"L1": 0.0, "L2": 0.0, "L3": 0.0}}
    return {
        "max_modules": 216,
        "modules": len({p for item in positions for p in range(item["start"], item["end"] + 1)}),
        "positions": positions,
        "groups": group_model,
        "phase_assignment": phases,
        "warnings": warnings,
    }
