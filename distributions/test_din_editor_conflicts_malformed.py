"""Tests for malformed DIN/KiCad conflict input."""
import pytest

from .din_editor_conflicts import build_conflict_list, resolve_conflicts


def test_build_conflict_list_ignores_malformed_kicad_fields():
    local = [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}]
    assert build_conflict_list(local, [None, "broken", {"reference": "X5", "label": "25V"}]) == [
        {"reference": "X5", "local_label": "24V", "kicad_label": "25V"}
    ]


@pytest.mark.parametrize("conflict", [None, "broken", {}, {"reference": "X5"}, {"kicad_label": "25V"}, {"reference": "", "kicad_label": "25V"}])
def test_resolve_conflicts_rejects_malformed_conflict(conflict):
    with pytest.raises(ValueError):
        resolve_conflicts(
            [{"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "24V"}],
            [conflict],
            choice="kicad",
        )
