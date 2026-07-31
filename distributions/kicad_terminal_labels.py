"""Carry user-editable terminal labels into the KiCad export manifest."""
from .kicad_symbol_manifest import build_symbol_manifest


def build_labeled_symbol_manifest(plan: dict) -> dict:
    manifest = build_symbol_manifest(plan)
    terminal_labels: dict[str, str] = {}
    ambiguous: set[str] = set()
    for terminal in plan.get("terminals", []):
        reference = str(terminal.get("reference", ""))
        label = str(terminal.get("label") or terminal.get("terminal_label") or reference)
        if reference in terminal_labels and terminal_labels[reference] != label:
            ambiguous.add(reference)
        else:
            terminal_labels[reference] = label

    for symbol in manifest["symbols"]:
        reference = str(symbol.get("reference", ""))
        if reference in terminal_labels and reference not in ambiguous:
            symbol["label"] = terminal_labels[reference]
            symbol["user_editable_label"] = True
    return manifest
