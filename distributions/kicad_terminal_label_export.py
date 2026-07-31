"""Export user-editable terminal labels as KiCad text-field metadata."""
from .kicad_terminal_labels import build_labeled_symbol_manifest


def terminal_label_fields(plan: dict) -> list[dict]:
    manifest = build_labeled_symbol_manifest(plan)
    return [
        {
            "reference": s["reference"],
            "label": s["label"],
            "field_name": "Terminal_Label",
            "user_editable": bool(s.get("user_editable_label")),
        }
        for s in manifest["symbols"]
        if s.get("user_editable_label")
    ]
