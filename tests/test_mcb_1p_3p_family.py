import json
from pathlib import Path

from tools.generate_device_variants import expand_series
from tools.generate_symbol_previews import (
    _logical_points,
    parse_pins,
    parse_polylines,
    symbol_blocks,
)
from tools.quality.kicad_symbol_adapter import extract_symbol_facts


MCB_PATH = Path("symbols/Z_MCB.kicad_sym")
SERIES_PATH = Path("data/device_series/generic/mcb-3p-template-series.yaml")
CURRENTS = (2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 125)
CURVES = ("B", "C", "D")


def _symbol_width_mm(block: str) -> float:
    points = _logical_points([], parse_pins(block), parse_polylines(block))
    xs = [point[0] for point in points]
    return max(xs) - min(xs)


def test_mcb_library_keeps_1p_id_and_adds_separate_3p_symbol():
    blocks = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))

    assert list(blocks) == ["MCB", "MCB_3P"]
    assert len(parse_pins(blocks["MCB"])) == 2
    assert len(parse_pins(blocks["MCB_3P"])) == 6
    assert parse_polylines(blocks["MCB"])
    assert parse_polylines(blocks["MCB_3P"])


def test_mcb_1p_uses_vertical_terminal_flow_1_to_2():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB"]
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (5.08, 7.62, 270.0, 2.54),
        (5.08, -7.62, 90.0, 2.54),
    ]
    assert '(number "1"' in block
    assert '(number "2"' in block


def test_mcb_1p_matches_reference_contact_trip_and_lower_terminal_shape():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB"]
    points = {polyline.points for polyline in parse_polylines(block)}

    assert ((5.08, 5.08), (5.08, 3.81)) in points
    assert ((1.27, 3.81), (5.08, -3.81)) in points
    assert ((5.08, -3.81), (5.08, -5.08)) in points
    assert (
        (-5.08, -1.27),
        (-3.81, -1.27),
        (-2.54, -2.54),
        (-1.27, -1.27),
        (3.81, -1.27),
    ) in points
    assert ((-1.27, 1.27), (0.0, 2.54), (0.0, 0.0), (-1.27, 1.27)) in points
    assert ((0.0, 1.27), (2.54, 1.27)) in points


def test_mcb_3p_uses_terminal_pairs_1_2_3_4_5_6():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    pins = parse_pins(block)

    assert [(pin.y, pin.angle) for pin in pins] == [
        (7.62, 270.0), (-7.62, 90.0),
        (7.62, 270.0), (-7.62, 90.0),
        (7.62, 270.0), (-7.62, 90.0),
    ]
    for number in ("1", "2", "3", "4", "5", "6"):
        assert f'(number "{number}"' in block


def test_mcb_3p_reuses_same_reference_contact_shape_on_all_three_poles():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    points = {polyline.points for polyline in parse_polylines(block)}

    for upper_x, slant_x, lower_x in (
        (-5.08, -8.89, -5.08),
        (2.54, -1.27, 2.54),
        (10.16, 6.35, 10.16),
    ):
        assert ((upper_x, 5.08), (upper_x, 3.81)) in points
        assert ((slant_x, 3.81), (lower_x, -3.81)) in points
        assert ((lower_x, -3.81), (lower_x, -5.08)) in points


def test_mcb_reference_widths_match_documented_400_and_800_mil_targets():
    blocks = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))

    assert round(_symbol_width_mm(blocks["MCB"]), 2) == 10.16
    assert round(_symbol_width_mm(blocks["MCB_3P"]), 2) == 20.32


def test_mcb_library_remains_z_geometry_conform():
    facts = extract_symbol_facts(MCB_PATH)

    assert facts["connection_grid_mil"] == 100
    assert facts["pin_length_mil"] == 100
    assert facts["line_width_mil"] == 10
    assert facts["text_size_mil"] == 50
    assert facts["footprint_policy"] == "optional"


def test_mcb_3p_series_contains_exact_requested_curve_current_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 42
    assert {(item["trip_curve"], item["rated_current_a"]) for item in devices} == {
        (curve, current) for curve in CURVES for current in CURRENTS
    }
    assert {item["symbol"] for item in devices} == {"Z_MCB:MCB_3P"}
    assert {item["poles"] for item in devices} == {3}
    assert {item["abbreviation"] for item in devices} == {"MCB"}
    assert all(item["name_de"].startswith("Leitungsschutzschalter ") for item in devices)
    assert all(item["name_en"].startswith("Miniature Circuit Breaker ") for item in devices)
