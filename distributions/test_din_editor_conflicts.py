"""Tests for deterministic DIN/KiCad conflict resolution."""
import pytest

from .din_editor_conflicts import build_conflict_list, resolve_conflicts


def test_conflict_resolution_rejects_ambiguous_kicad_values():
    conflicts = [
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V A"},
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V B"},
    ]

    with pytest.raises(ValueError, match="ambiguous KiCad conflict for reference X5"):
        resolve_conflicts(
            [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}],
            conflicts,
            choice="kicad",
        )


def test_conflict_resolution_accepts_duplicate_identical_kicad_values():
    conflicts = [
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V A"},
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V A"},
    ]

    result = resolve_conflicts(
        [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}],
        conflicts,
        choice="kicad",
    )

    assert result[0]["label"] == "24V A"


def test_local_choice_never_applies_ambiguous_kicad_values():
    conflicts = [
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V A"},
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V B"},
    ]

    result = resolve_conflicts(
        [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}],
        conflicts,
        choice="local",
    )

    assert result[0]["label"] == "24V"


def test_build_conflict_list_reports_each_incoming_conflict():
    local = [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}]
    fields = [{"reference": "X5", "label": "24V A"}, {"reference": "X5", "label": "24V B"}]

    assert build_conflict_list(local, fields) == [
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V A"},
        {"reference": "X5", "local_label": "24V", "kicad_label": "24V B"},
    ]
