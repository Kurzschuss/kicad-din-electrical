"""Validate synchronization between DIN editor data and KiCad terminal labels."""
from .kicad_terminal_label_export import terminal_label_fields


def terminal_sync_report(components: list[dict]) -> dict:
    plan = {"components": [dict(c) for c in components]}
    fields = terminal_label_fields(plan)
    expected = {}
    conflicts = []
    for field in fields:
        reference = str(field["reference"])
        label = str(field["label"])
        if reference in expected and expected[reference] != label:
            conflicts.append({"reference": reference, "labels": [expected[reference], label]})
        expected[reference] = label
    missing = [
        str(c.get("reference"))
        for c in components
        if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK"
        and c.get("can_edit_label", True)
        and not str(c.get("label") or c.get("terminal_label") or "").strip()
    ]
    return {"valid": not conflicts and not missing, "fields": fields, "conflicts": conflicts, "missing_labels": missing}
