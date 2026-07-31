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


def kicad_manifest_terminal_fields(manifest: dict) -> list[dict]:
    """Extract only editable Terminal_Label fields from a KiCad symbol manifest."""
    if not isinstance(manifest, dict):
        raise ValueError("KiCad manifest must be an object")
    symbols = manifest.get("symbols", [])
    if not isinstance(symbols, list):
        raise ValueError("KiCad manifest symbols must be a list")
    fields = []
    for symbol in symbols:
        if not isinstance(symbol, dict) or not symbol.get("user_editable_label"):
            continue
        reference = str(symbol.get("reference", "")).strip()
        label = str(symbol.get("label", "")).strip()
        if reference and label:
            fields.append({"reference": reference, "label": label, "field_name": "Terminal_Label", "user_editable": True})
    return fields


def apply_kicad_terminal_labels(components: list[dict], fields: list[dict], *, overwrite: bool = True) -> list[dict]:
    """Apply unambiguous KiCad Terminal_Label fields to matching DIN terminal blocks."""
    labels: dict[str, str] = {}
    ambiguous: set[str] = set()
    for field in fields:
        reference = str(field.get("reference", ""))
        label = str(field.get("label", "")).strip()
        if reference in labels and labels[reference] != label:
            ambiguous.add(reference)
        else:
            labels[reference] = label

    result = [dict(c) for c in components]
    for item in result:
        reference = str(item.get("reference", ""))
        if item.get("component_type") != "DIN_RAIL_TERMINAL_BLOCK" or reference not in labels or reference in ambiguous:
            continue
        label = labels[reference]
        if label and (overwrite or not str(item.get("label") or item.get("terminal_label") or "").strip()):
            item["label"] = label
            item["terminal_label"] = label
            item["can_edit_label"] = True
    return result


def import_kicad_manifest_labels(components: list[dict], manifest: dict, *, overwrite: bool = True) -> list[dict]:
    """Import editable terminal labels from a KiCad manifest into editor components."""
    fields = kicad_manifest_terminal_fields(manifest)
    return apply_kicad_terminal_labels(components, fields, overwrite=overwrite)


def export_terminal_labels(components: list[dict]) -> list[dict]:
    return terminal_label_fields({"components": [dict(c) for c in components]})
