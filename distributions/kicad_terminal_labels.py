"""Carry user-editable terminal labels into the KiCad export manifest."""
from .kicad_symbol_manifest import build_symbol_manifest


def build_labeled_symbol_manifest(plan: dict) -> dict:
    manifest = build_symbol_manifest(plan)
    terminal_labels = {
        str(t.get("reference")): str(t.get("label") or t.get("terminal_label") or t.get("reference"))
        for t in plan.get("terminals", [])
    }
    for symbol in manifest["symbols"]:
        reference = str(symbol.get("reference"))
        if reference in terminal_labels:
            symbol["label"] = terminal_labels[reference]
            symbol["user_editable_label"] = True
    return manifest
