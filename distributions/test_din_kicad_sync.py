"""Tests for bidirectional KiCad terminal-label synchronization."""
import pytest

from .din_kicad_sync import (
    apply_kicad_terminal_labels,
    export_terminal_labels,
    import_kicad_manifest_labels,
    kicad_manifest_terminal_fields,
    terminal_sync_report,
)


def _components():
    return [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
        {"reference": "R1", "component_type": "RESISTOR", "label": "10k", "can_edit_label": False},
    ]


def test_manifest_extracts_only_editable_nonempty_labels():
    manifest = {"symbols": [
        {"reference": "X5", "label": "24V", "user_editable_label": True},
        {"reference": "X6", "label": "", "user_editable_label": True},
        {"reference": "R1", "label": "10k", "user_editable_label": False},
        "invalid",
    ]}
    assert kicad_manifest_terminal_fields(manifest) == [{
        "reference": "X5", "label": "24V", "field_name": "Terminal_Label", "user_editable": True,
    }]


def test_manifest_rejects_invalid_shape():
    with pytest.raises(ValueError, match="manifest must be an object"):
        kicad_manifest_terminal_fields([])
    with pytest.raises(ValueError, match="symbols must be a list"):
        kicad_manifest_terminal_fields({"symbols": {}})


def test_apply_updates_matching_terminal_and_preserves_other_components():
    result = apply_kicad_terminal_labels(_components(), [{"reference": "X5", "label": "24V"}])
    assert result[0]["label"] == "24V"
    assert result[0]["terminal_label"] == "24V"
    assert result[2] == _components()[2]


def test_apply_can_keep_existing_label_when_overwrite_disabled():
    result = apply_kicad_terminal_labels(_components(), [{"reference": "X5", "label": "24V"}], overwrite=False)
    assert result[0]["label"] == "+24V SPS"


def test_apply_ignores_ambiguous_reference():
    fields = [{"reference": "X5", "label": "24V"}, {"reference": "X5", "label": "0V"}]
    result = apply_kicad_terminal_labels(_components(), fields)
    assert result[0]["label"] == "+24V SPS"


def test_apply_accepts_duplicate_identical_values():
    fields = [{"reference": "X5", "label": "24V"}, {"reference": "X5", "label": "24V"}]
    result = apply_kicad_terminal_labels(_components(), fields)
    assert result[0]["label"] == "24V"
    assert result[0]["terminal_label"] == "24V"


def test_import_manifest_is_composed_from_extract_and_apply():
    manifest = {"symbols": [{"reference": "X5", "label": "24V", "user_editable_label": True}]}
    result = import_kicad_manifest_labels(_components(), manifest)
    assert result[0]["label"] == "24V"


def test_export_returns_terminal_label_fields():
    assert export_terminal_labels(_components()) == [
        {"reference": "X5", "label": "+24V SPS", "field_name": "Terminal_Label", "user_editable": True},
        {"reference": "X6", "label": "0V SPS", "field_name": "Terminal_Label", "user_editable": True},
    ]


def test_sync_report_detects_missing_and_duplicate_terminal_labels():
    components = [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V", "can_edit_label": True},
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "", "can_edit_label": True},
    ]
    report = terminal_sync_report(components)
    assert not report["valid"]
    assert "X6" in report["missing_labels"]
    assert any(conflict["reference"] == "X5" for conflict in report["conflicts"])


def test_sync_report_accepts_valid_terminal_components():
    report = terminal_sync_report(_components())
    assert report["valid"]
    assert report["conflicts"] == []
    assert report["missing_labels"] == []
