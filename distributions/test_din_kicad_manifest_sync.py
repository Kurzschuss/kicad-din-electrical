"""Tests for importing editable labels from a KiCad symbol manifest."""
import pytest

from .din_kicad_sync import import_kicad_manifest_labels, kicad_manifest_terminal_fields


def _components():
    return [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ]


def test_manifest_import_updates_only_editable_terminal_labels():
    manifest = {
        "format": "kicad-symbol-manifest",
        "symbols": [
            {"reference": "X5", "label": "Versorgung 24V", "user_editable_label": True},
            {"reference": "Q1", "label": "Nicht importieren", "user_editable_label": False},
            {"reference": "X99", "label": "Unbekannt", "user_editable_label": True},
        ],
    }

    result = import_kicad_manifest_labels(_components(), manifest)

    assert result[0]["label"] == "Versorgung 24V"
    assert result[0]["terminal_label"] == "Versorgung 24V"
    assert result[1]["label"] == "0V SPS"


def test_manifest_import_can_preserve_existing_editor_label():
    manifest = {"symbols": [{"reference": "X5", "label": "KiCad", "user_editable_label": True}]}

    result = import_kicad_manifest_labels(_components(), manifest, overwrite=False)

    assert result[0]["label"] == "+24V SPS"


def test_manifest_fields_ignore_non_editable_and_malformed_symbols():
    manifest = {
        "symbols": [
            {"reference": "X5", "label": "24V", "user_editable_label": True},
            {"reference": "X6", "label": "0V", "user_editable_label": False},
            {"reference": "X7", "label": "", "user_editable_label": True},
            "broken",
        ]
    }

    assert kicad_manifest_terminal_fields(manifest) == [
        {"reference": "X5", "label": "24V", "field_name": "Terminal_Label", "user_editable": True}
    ]


@pytest.mark.parametrize("manifest", [None, [], {"symbols": {}}])
def test_manifest_import_rejects_invalid_manifest_shape(manifest):
    with pytest.raises(ValueError):
        kicad_manifest_terminal_fields(manifest)
