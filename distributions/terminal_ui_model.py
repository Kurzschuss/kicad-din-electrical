"""Editable UI model for terminal labels and validation feedback."""
from .terminal_labels import apply_terminal_labels
from .terminal_validation import validate_terminal_labels


def editable_terminals(terminals: list[dict], schema: dict | None = None) -> list[dict]:
    labeled = apply_terminal_labels(terminals, schema)
    validated = validate_terminal_labels(labeled)
    return [
        {
            **item,
            "editable_label": item["terminal_label"],
            "can_edit_label": True,
            "validation_ok": item["terminal_label_valid"],
            "validation_errors": item["terminal_label_errors"],
        }
        for item in validated
    ]
