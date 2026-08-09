import json
from pathlib import Path

import pytest

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
    assert ((-5.08, 0.0), (-5.08, -2.54)) in points
    assert (
        (-5.08, -1.27),
        (-3.81, -1.27),
        (-2.54, -2.54),
        (-1.27, -1.27),
        (3.81, -1.27),
    ) in points


def test_mcb_1p_left_end_stop_is_centered_on_horizontal_trip_line():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB"]
    points = {polyline.points for polyline in parse_polylines(block)}
    end_stop = ((-5.08, 0.0), (-5.08, -2.54))

    assert end_stop in points
    midpoint_y = (end_stop[0][1] + end_stop[1][1]) / 2.0
    assert midpoint_y == pytest.approx(-1.27)


def test_mcb_1p_trip_arrow_is_shorter_but_still_touches_switch_contact():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB"]
    points = {polyline.points for polyline in parse_polylines(block)}
    arrowhead = (
        (-1.518, -0.083),
        (-0.237, 1.135),
        (0.237, -0.289),
        (-1.518, -0.083),
    )
    shaft = ((0.0, 0.423), (2.54, 1.27))

    assert arrowhead in points
    assert shaft in points
    assert shaft[1] == pytest.approx((2.54, 1.27))
    assert shaft[1][0] - shaft[0][0] == pytest.approx(2.54)
    # Pfeilkopf bleibt gedreht und behält Luft zur waagrechten Betätigungslinie.
    assert arrowhead[1][0] != pytest.approx(arrowhead[2][0])
    assert min(y for _, y in arrowhead) - (-1.27) > 0.5
    # Der Schaft endet wieder exakt auf dem schrägen Schaltkontakt.
    assert ((1.27, 3.81), (5.08, -3.81)) in points


def test_mcb_3p_uses_terminal_pairs_with_300_mil_pole_pitch():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (5.08, 7.62, 270.0, 2.54),
        (5.08, -7.62, 90.0, 2.54),
        (12.7, 7.62, 270.0, 2.54),
        (12.7, -7.62, 90.0, 2.54),
        (20.32, 7.62, 270.0, 2.54),
        (20.32, -7.62, 90.0, 2.54),
    ]
    assert pins[2].x - pins[0].x == pytest.approx(7.62)
    assert pins[4].x - pins[2].x == pytest.approx(7.62)
    for number in ("1", "2", "3", "4", "5", "6"):
        assert f'(number "{number}"' in block


def test_mcb_3p_reuses_full_1p_reference_shape_on_first_pole():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    points = {polyline.points for polyline in parse_polylines(block)}

    assert ((-5.08, 0.0), (-5.08, -2.54)) in points
    assert (
        (-5.08, -1.27),
        (-3.81, -1.27),
        (-2.54, -2.54),
        (-1.27, -1.27),
        (3.81, -1.27),
    ) in points

    for terminal_x, slant_x in ((5.08, 1.27), (12.7, 8.89), (20.32, 16.51)):
        assert ((terminal_x, 5.08), (terminal_x, 3.81)) in points
        assert ((slant_x, 3.81), (terminal_x, -3.81)) in points
        assert ((terminal_x, -3.81), (terminal_x, -5.08)) in points


def test_mcb_3p_trip_arrows_are_shorter_and_touch_each_switch_contact():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    points = {polyline.points for polyline in parse_polylines(block)}

    arrowheads = (
        ((-1.518, -0.083), (-0.237, 1.135), (0.237, -0.289), (-1.518, -0.083)),
        ((6.102, -0.083), (7.383, 1.135), (7.857, -0.289), (6.102, -0.083)),
        ((13.722, -0.083), (15.003, 1.135), (15.477, -0.289), (13.722, -0.083)),
    )
    shafts = (
        ((0.0, 0.423), (2.54, 1.27)),
        ((7.62, 0.423), (10.16, 1.27)),
        ((15.24, 0.423), (17.78, 1.27)),
    )
    expected_contact_points = ((2.54, 1.27), (10.16, 1.27), (17.78, 1.27))

    for arrowhead, shaft, contact_point in zip(arrowheads, shafts, expected_contact_points):
        assert arrowhead in points
        assert shaft in points
        assert shaft[1] == pytest.approx(contact_point)
        assert shaft[1][0] - shaft[0][0] == pytest.approx(2.54)
        assert arrowhead[1][0] != pytest.approx(arrowhead[2][0])
        assert min(y for _, y in arrowhead) - (-1.27) > 0.5


def test_mcb_3p_coupling_marks_are_longer_solid_line_per_gap():
    block = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))["MCB_3P"]
    points = {polyline.points for polyline in parse_polylines(block)}

    assert ((5.715, -1.27), (7.62, -1.27)) in points
    assert ((13.335, -1.27), (15.24, -1.27)) in points
    coupling_marks = [
        polyline for polyline in parse_polylines(block)
        if len(polyline.points) == 2
        and all(y == pytest.approx(-1.27) for _, y in polyline.points)
        and abs(polyline.points[1][0] - polyline.points[0][0]) == pytest.approx(1.905)
    ]
    assert len(coupling_marks) == 2
    assert 8.89 - 7.62 == pytest.approx(1.27)
    assert 16.51 - 15.24 == pytest.approx(1.27)
    assert "(type dash)" not in block


def test_mcb_reference_widths_include_documented_3p_geometry_exception():
    blocks = symbol_blocks(MCB_PATH.read_text(encoding="utf-8"))

    assert round(_symbol_width_mm(blocks["MCB"]), 2) == 10.16  # 400 mil
    assert round(_symbol_width_mm(blocks["MCB_3P"]), 2) == 25.40  # 1000 mil, dokumentierte Ausnahme


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
