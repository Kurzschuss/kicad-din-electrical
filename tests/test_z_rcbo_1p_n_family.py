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


RCBO_PATH = Path("symbols/Z_RCBO_1P_N.kicad_sym")
TYPE_A_SERIES_PATH = Path("data/device_series/generic/rcbo-1p-n-type-a-template-series.yaml")
TYPE_F_SERIES_PATH = Path("data/device_series/generic/rcbo-1p-n-type-f-template-series.yaml")
TYPE_A_CURRENTS = (6, 10, 16, 20, 25, 32, 40)
TYPE_A_CURVES = ("B", "C")


def rcbo_block() -> str:
    return symbol_blocks(RCBO_PATH.read_text(encoding="utf-8"))["RCBO_1P_N"]


def test_rcbo_symbol_has_1p_n_terminals_and_neutral_marking():
    block = rcbo_block()
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 12.7, 270.0, 2.54),
        (0.0, -12.7, 90.0, 2.54),
        (7.62, 12.7, 270.0, 2.54),
        (7.62, -12.7, 90.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4"]
    assert parse_pin_names(block) == ["~", "~", "N", "N"]


def test_rcbo_symbol_combines_overcurrent_and_residual_current_functions():
    block = rcbo_block()
    points = {polyline.points for polyline in parse_polylines(block)}
    rectangles = parse_rectangles(block)
    labels = {(item.value, item.x, item.y) for item in parse_texts(block)}

    assert ("T", -15.24, 7.62) in labels
    assert ("I>", 16.51, -2.032) in labels
    assert ("IΔ", 16.51, -5.588) in labels
    assert any(item.dashed for item in parse_polylines(block))

    for x in (0.0, 7.62):
        assert ((x, 10.16), (x, 8.89)) in points
        assert ((x - 2.54, 8.89), (x, 3.81)) in points
        assert ((x, 3.81), (x, -10.16)) in points

    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (-2.54, 0.0, 10.16, -5.08)
        for item in rectangles
    )
    assert any(
        item.filled
        and (item.x1, item.y1, item.x2, item.y2) == (-2.54, 0.0, -1.27, -5.08)
        for item in rectangles
    )
    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (12.7, 0.0, 20.32, -7.62)
        for item in rectangles
    )


def test_rcbo_preview_is_generated_from_supported_geometry():
    block = rcbo_block()
    svg = render_svg(
        "Z_RCBO_1P_N",
        "RCBO_1P_N",
        parse_rectangles(block),
        parse_pins(block),
        parse_polylines(block),
        parse_pin_numbers(block),
        parse_pin_names(block),
        parse_texts(block),
    )

    assert "<title>Z_RCBO_1P_N: RCBO_1P_N</title>" in svg
    assert "<rect " in svg
    assert "<polyline " in svg
    assert "<polygon " in svg
    assert svg.count("<line ") == 4
    assert ">RCBO_1P_N</text>" in svg


def test_rcbo_symbol_reference_metadata_is_complete():
    block = rcbo_block()
    expected_properties = {
        "Z_Footprint_Policy": "optional",
        "Z_Poles": "2",
        "Z_Protected_Poles": "1",
        "Z_Rated_Current_A": "16",
        "Z_Trip_Curve": "B",
        "Z_Residual_Current_mA": "30",
        "Z_RCD_Type": "A",
        "Z_Breaking_Capacity_kA": "6",
        "Z_Test_Button": "present",
    }
    for name, value in expected_properties.items():
        assert f'(property "{name}" "{value}"' in block


def test_rcbo_type_a_series_contains_expected_planning_matrix():
    series = json.loads(TYPE_A_SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 14
    assert {
        (item["rated_current_a"], item["trip_curve"])
        for item in devices
    } == {
        (current, curve)
        for current in TYPE_A_CURRENTS
        for curve in TYPE_A_CURVES
    }
    assert {item["residual_current_ma"] for item in devices} == {30}
    assert {item["rcd_type"] for item in devices} == {"A"}
    assert {item["breaking_capacity_ka"] for item in devices} == {6}
    assert {item["symbol"] for item in devices} == {"Z_RCBO_1P_N:RCBO_1P_N"}
    assert {item["poles"] for item in devices} == {2}
    assert {item["modules"] for item in devices} == {2}
    assert {item["footprint_policy"] for item in devices} == {"optional"}


def test_rcbo_type_f_series_is_deliberately_conservative():
    series = json.loads(TYPE_F_SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 2
    assert {
        (item["rated_current_a"], item["trip_curve"], item["residual_current_ma"], item["rcd_type"], item["breaking_capacity_ka"])
        for item in devices
    } == {
        (6, "C", 30, "F", 6),
        (16, "C", 30, "F", 6),
    }
    assert {item["symbol"] for item in devices} == {"Z_RCBO_1P_N:RCBO_1P_N"}
    assert {item["modules"] for item in devices} == {2}
