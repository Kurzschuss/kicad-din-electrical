"""Tests for user-editable terminal labels in the KiCad export manifest."""
from .kicad_terminal_labels import build_labeled_symbol_manifest


def test_labeled_manifest_uses_terminal_label():
    plan = {
        "name": "Test",
        "components": [],
        "terminals": [{"reference": "X5", "label": "Versorgung 24V"}],
    }

    manifest = build_labeled_symbol_manifest(plan)
    symbol = next(item for item in manifest["symbols"] if item["reference"] == "X5")

    assert symbol["label"] == "Versorgung 24V"
    assert symbol["user_editable_label"] is True


def test_labeled_manifest_skips_conflicting_terminal_reference():
    plan = {
        "name": "Test",
        "components": [],
        "terminals": [
            {"reference": "X5", "label": "24V A"},
            {"reference": "X5", "label": "24V B"},
        ],
    }

    manifest = build_labeled_symbol_manifest(plan)
    symbol = next(item for item in manifest["symbols"] if item["reference"] == "X5")

    assert symbol["label"] == "24V A"
    assert "user_editable_label" not in symbol
