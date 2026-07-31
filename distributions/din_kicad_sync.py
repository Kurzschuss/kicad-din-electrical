"""Bidirectional synchronization helpers for DIN editor terminal labels."""
from .kicad_terminal_label_export import terminal_label_fields


def terminal_sync_report(components: list[dict]) -> dict:
    fields = terminal_label_fields({"components": [dict(c) for c in components]})
    expected = {}
    conflicts = []
    for field in fields:
        reference = str(field["reference"])
        label = str(field["label"])
        if reference in expected and expected[reference] != label:
            conflicts.append({"reference": reference, "labels": [expected[reference], label]})
        expected[reference] = label
    missing = [str(c.get("reference")) for c in components if c.get("component_type") == "DIN_RAIL_TERMINAL_BLOCK" and c.get("can_edit_label", True) and not str(c.get("label") or c.get("terminal_label") or "").strip()]
    return {"valid": not conflicts and not missing, "fields": fields, "conflicts": conflicts, "missing_labels": missing}


def apply_kicad_terminal_labels(components: list[dict], fields: list[dict], *, overwrite: bool = True) -> list[dict]:
    """Apply KiCad Terminal_Label fields back to matching DIN terminal blocks."""
    labels = {str(field.get("reference")): str(field.get("label", "")).strip() for field in fields}
    result = [dict(c) for c in components]
    for item in result:
        reference = str(item.get("reference", ""))
        if item.get("component_type") != "DIN_RAIL_TERMINAL_BLOCK" or reference not in labels:
            continue
        label = labels[reference]
        if label and (overwrite or not str(item.get("label") or item.get("terminal_label") or "").strip()):
            item["label"] = label
            item["terminal_label"] = label
            item["can_edit_label"] = True
    return result


def export_terminal_labels(components: list[dict]) -> list[dict]:
    return terminal_label_fields({"components": [dict(c) for c in components]})
