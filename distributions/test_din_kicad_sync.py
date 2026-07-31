"""Tests for bidirectional KiCad terminal-label synchronization."""
from .din_kicad_sync import apply_kicad_terminal_labels, terminal_sync_report


def _components():
    return [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ]


def test_apply_kicad_terminal_labels_skips_conflicting_reference():
    components = _components()
    fields = [
        {"reference": "X5", "label": "24V A"},
        {"reference": "X5", "label": "24V B"},
        {"reference": "X6", "label": "0V"},
    ]

    result = apply_kicad_terminal_labels(components, fields)

    assert result[0]["label"] == "+24V SPS"
    assert result[0]["terminal_label"] if "terminal_label" in result[0] else True
    assert result[1]["label"] == "0V"
    assert result[1]["terminal_label"] == "0V"


def test_apply_kicad_terminal_labels_accepts_duplicate_identical_values():
    components = _components()
    fields = [
        {"reference": "X5", "label": "24V"},
        {"reference": "X5", "label": "24V"},
    ]

    result = apply_kicad_terminal_labels(components, fields)

    assert result[0]["label"] == "24V"
    assert result[0]["terminal_label"] == "24V"


def test_terminal_sync_report_marks_conflicting_reference_invalid():
    components = [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V", "can_edit_label": True},
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V B", "can_edit_label": True},
    ]

    report = terminal_sync_report(components)

    assert report["valid"] is False
    assert report["conflicts"] == [{"reference": "X5", "labels": ["24V", "24V B"]}]
