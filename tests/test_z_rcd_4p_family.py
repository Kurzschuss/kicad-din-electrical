import json
from pathlib import Path

from tools.generate_device_variants import expand_series
from tools.generate_symbol_previews import (
    parse_pin_names,
    parse_pin_numbers,
    parse_pins,
    parse_polylines,
    parse_rectangles,
    parse_texts,
    render_svg,
    symbol_blocks,
)


RCD_PATH = Path("symbols/Z_RCD.kicad_sym")
SERIES_PATH = Path("data/device_series/generic/rcd-4p-template-series.yaml")
CURRENTS = (25, 40, 63, 125)
RESIDUAL_CURRENTS = (30, 300, 500)
RCD_TYPES = ("A", "B", "B+")
SHORT_CIRCUIT_CURRENTS = (6, 10)


def rcd_4p_block() -> str:
    return symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD_4P"]


def test_rcd_4p_symbol_has_four_poles_and_eight_terminals():
    block = rcd_4p_block()
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 12.7, 270.0, 2.54),
        (0.0, -12.7, 90.0, 2.54),
        (7.62, 12.7, 270.0, 2.54),
        (7.62, -12.7, 90.0, 2.54),
        (15.24, 12.7, 270.0, 2.54),
        (15.24, -12.7, 90.0, 2.54),
        (22.86, 12.7, 270.0, 2.54),
        (22.86, -12.7, 90.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4", "5", "6", "7", "8"]
    assert parse_pin_names(block) == ["~", "~", "~", "~", "~", "~", "N", "N"]


def test_rcd_4p_symbol_matches_approved_reference_geometry():
    block = rcd_4p_block()
    points = {polyline.points for polyline in parse_polylines(block)}
    rectangles = parse_rectangles(block)
    labels = {(item.value, item.x, item.y) for item in parse_texts(block)}

    for x in (0.0, 7.62, 15.24, 22.86):
        assert ((x, 10.16), (x, 8.89)) in points
        assert ((x - 2.54, 8.89), (x, 3.81)) in points
        assert ((x, 3.81), (x, -10.16)) in points

    assert ((-5.08, 6.35), (33.02, 6.35)) in points
    assert any(item.dashed for item in parse_polylines(block))
    assert ("T", -22.86, 8.89) in labels
    assert ("E", -22.86, 5.08) in labels

    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (-5.08, 0.0, 30.48, -5.08)
        for item in rectangles
    )
    assert any(
        item.filled
        and (item.x1, item.y1, item.x2, item.y2) == (-5.08, 0.0, -1.27, -5.08)
        for item in rectangles
    )
    assert ((-1.27, -2.54), (30.48, -2.54)) in points

    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (33.02, 8.89, 39.37, 3.81)
        for item in rectangles
    )
    assert ((36.195, 8.89), (36.195, 3.81)) in points
    assert ((33.02, 6.35), (39.37, 6.35)) in points


def test_rcd_4p_preview_preserves_dashes_fill_labels_and_neutral_marking():
    block = rcd_4p_block()
    svg = render_svg(
        "Z_RCD",
        "RCD_4P",
        parse_rectangles(block),
        parse_pins(block),
        parse_polylines(block),
        parse_pin_numbers(block),
        parse_pin_names(block),
        parse_texts(block),
    )

    assert 'stroke-dasharray="8 6"' in svg
    assert 'fill="currentColor"' in svg
    assert ">T</text>" in svg
    assert ">E</text>" in svg
    for number in ("1", "2", "3", "4", "5", "6", "7", "8"):
        assert f">{number}</text>" in svg
    assert svg.count(">N</text>") == 2


def test_rcd_4p_symbol_reference_metadata_contains_requested_ratings():
    block = rcd_4p_block()
    expected_properties = {
        "Z_Poles": "4",
        "Z_Rated_Current_A": "40",
        "Z_Residual_Current_mA": "30",
        "Z_RCD_Type": "A",
        "Z_Rated_Short_Circuit_Current_kA": "6",
        "Z_Making_Breaking_Capacity_kA": "1.5",
        "Z_Test_Button": "present",
    }
    for name, value in expected_properties.items():
        assert f'(property "{name}" "{value}"' in block


def test_rcd_4p_series_contains_exact_requested_variant_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 72
    assert {
        (
            item["rated_current_a"],
            item["residual_current_ma"],
            item["rcd_type"],
            item["rated_short_circuit_current_ka"],
        )
        for item in devices
    } == {
        (current, residual, rcd_type, short_circuit)
        for current in CURRENTS
        for residual in RESIDUAL_CURRENTS
        for rcd_type in RCD_TYPES
        for short_circuit in SHORT_CIRCUIT_CURRENTS
    }
    assert {item["making_breaking_capacity_ka"] for item in devices} == {1.5}
    assert {item["symbol"] for item in devices} == {"Z_RCD:RCD_4P"}
    assert {item["poles"] for item in devices} == {4}
    assert {item["modules"] for item in devices} == {4}
