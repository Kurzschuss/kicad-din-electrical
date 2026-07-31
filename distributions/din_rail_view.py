"""Build a UI-friendly representation of DIN rails and occupied TE slots."""
from .din_rail_layout import MAX_TE_PER_RAIL, DEFAULT_RAILS, component_te


def build_rail_view(components: list[dict], rails: int = DEFAULT_RAILS, te_per_rail: int = MAX_TE_PER_RAIL) -> list[dict]:
    """Return one row per rail with 1-based TE slots and component occupancy."""
    rows = []
    for rail in range(1, int(rails) + 1):
        slots = []
        for te in range(1, int(te_per_rail) + 1):
            slots.append({"te": te, "reference": None, "label": None, "width_te": 0})
        for component in components:
            if int(component.get("rail", 1)) != rail:
                continue
            start = int(component.get("start_te", 1))
            end = int(component.get("end_te", start + component_te(component) - 1))
            label = component.get("label") or component.get("terminal_label") or component.get("value") or component.get("reference")
            for te in range(max(1, start), min(int(te_per_rail), end) + 1):
                slots[te - 1] = {
                    "te": te,
                    "reference": component.get("reference"),
                    "label": label,
                    "width_te": end - start + 1,
                    "start_te": start,
                    "end_te": end,
                }
        rows.append({"rail": rail, "te_per_rail": int(te_per_rail), "slots": slots})
    return rows
