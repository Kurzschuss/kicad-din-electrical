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
SERIES_PATH = Path("data/device_series/generic/rcd-2p-template-series.yaml")
CURRENTS = (16, 25, 40, 63)
RESIDUAL_CURRENTS = (10, 30, 300, 500)
RCD_TYPES = ("A", "F")
SHORT_CIRCUIT_CURRENTS = (6, 10)


def test_rcd_symbol_uses_vertical_two_pole_terminal_flow():
    block = symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD"]
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 12.7, 270.0, 2.54),
        (0.0, -12.7, 90.0, 2.54),
        (7.62, 12.7, 270.0, 2.54),
        (7.62, -12.7, 90.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4"]
    assert parse_pin_names(block) == ["~", "~", "N", "N"]


def test_rcd_symbol_matches_approved_switch_and_test_circuit_geometry():
    block = symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD"]
    points = {polyline.points for polyline in parse_polylines(block)}
    rectangles = parse_rectangles(block)
    texts = parse_texts(block)

    assert ((0.0, 10.16), (0.0, 8.89)) in points
    assert ((-2.54, 8.89), (0.0, 3.81)) in points
    assert ((0.0, 3.81), (0.0, -10.16)) in points
    assert ((7.62, 10.16), (7.62, 8.89)) in points
    assert ((5.08, 8.89), (7.62, 3.81)) in points
    assert ((7.62, 3.81), (7.62, -10.16)) in points

    # Die mechanische Kopplung liegt mittig durch die beiden Hauptkontakte.
    assert ((-5.08, 6.35), (22.86, 6.35)) in points
    assert (8.89 + 3.81) / 2 == 6.35

    # Der Testkontakt über dem verlängerten Widerstand ist auf dieselbe Höhe gesetzt.
    assert ((-20.32, 5.08), (-17.78, 5.08)) in points
    assert ((-17.78, 8.89), (-15.24, 3.81)) in points
    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (-16.51, 0.0, -13.97, -5.08)
        for item in rectangles
    )
    assert (
        (-15.24, -5.08),
        (-15.24, -8.89),
        (7.62, -8.89),
    ) in points
    assert any(item.value == "T" and item.x == -20.32 and item.y == 7.62 for item in texts)
    assert any(
        item.dashed and item.points == ((-5.08, 6.35), (22.86, 6.35))
        for item in parse_polylines(block)
    )


def test_rcd_symbol_matches_approved_residual_trip_geometry():
    block = symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD"]
    points = {polyline.points for polyline in parse_polylines(block)}
    rectangles = parse_rectangles(block)

    # Summenstromwandler und Auslöseblock liegen gegenüber dem vorherigen Stand tiefer.
    assert any(
        item.filled
        and (item.x1, item.y1, item.x2, item.y2) == (13.97, 0.0, 15.24, -5.08)
        for item in rectangles
    )
    assert ((12.7, 1.27), (17.78, 1.27), (17.78, -1.27), (16.51, -1.27)) in points
    assert ((17.78, -1.27), (20.32, -1.27)) in points
    assert ((17.78, -3.81), (20.32, -3.81)) in points
    assert ((27.94, -2.54), (29.21, -3.81), (27.94, -5.08)) in points

    # Das Kreuz im oberen Kasten ist exakt auf Höhe der gestrichelten Kopplung zentriert.
    assert ((26.035, 3.81), (26.035, 0.0)) in points
    assert ((22.86, 6.35), (29.21, 6.35)) in points
    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (22.86, 8.89, 29.21, 3.81)
        for item in rectangles
    )
    assert (8.89 + 3.81) / 2 == 6.35


def test_rcd_preview_preserves_reference_dashes_fill_and_terminal_labels():
    block = symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD"]
    svg = render_svg(
        "Z_RCD",
        "RCD",
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
    assert ">1</text>" in svg
    assert ">2</text>" in svg
    assert ">3</text>" in svg
    assert ">4</text>" in svg
    assert svg.count(">N</text>") == 2


def test_rcd_symbol_reference_metadata_contains_requested_ratings():
    text = RCD_PATH.read_text(encoding="utf-8")

    expected_properties = {
        "Z_Poles": "2",
        "Z_Rated_Current_A": "40",
        "Z_Residual_Current_mA": "30",
        "Z_RCD_Type": "A",
        "Z_Rated_Short_Circuit_Current_kA": "6",
        "Z_Making_Breaking_Capacity_kA": "1.5",
        "Z_Test_Button": "present",
    }
    for name, value in expected_properties.items():
        assert f'(property "{name}" "{value}"' in text


def test_rcd_2p_series_contains_exact_requested_variant_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 64
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
    assert {item["symbol"] for item in devices} == {"Z_RCD:RCD"}
    assert {item["poles"] for item in devices} == {2}
