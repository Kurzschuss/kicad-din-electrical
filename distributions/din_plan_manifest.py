"""Stable manifest for a complete DIN distribution plan."""

MAX_TE = 216
RAILS = 18
TE_PER_RAIL = 12


def make_plan(name: str = "DIN-Verteiler", components: list[dict] | None = None, terminals: list[dict] | None = None) -> dict:
    return {
        "name": name,
        "capacity_te": MAX_TE,
        "rails": RAILS,
        "te_per_rail": TE_PER_RAIL,
        "components": [dict(c) for c in (components or [])],
        "terminals": [dict(t) for t in (terminals or [])],
    }


def plan_used_te(plan: dict) -> int:
    return sum(int(c.get("width_te", 1)) for c in plan.get("components", [])) + sum(int(t.get("width_te", 1)) for t in plan.get("terminals", []))


def plan_remaining_te(plan: dict) -> int:
    return int(plan.get("capacity_te", MAX_TE)) - plan_used_te(plan)


def validate_plan(plan: dict) -> dict:
    used = plan_used_te(plan)
    capacity = int(plan.get("capacity_te", MAX_TE))
    return {"valid": used <= capacity, "capacity_te": capacity, "used_te": used, "remaining_te": capacity - used}
