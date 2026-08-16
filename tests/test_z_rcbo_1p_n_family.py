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
TYPE_A_CURRENTS = (6, 10, 13, 16, 20, 25, 32, 40)
TYPE_A_CURVES = ("B", "C")
TYPE_A_RESIDUAL_CURRENTS_MA = (10, 30)
TYPE_A_BREAKING_CAPACITIES_KA = (6, 10)


def rcbo_block() -> str:
    return symbol_blocks(RCBO_PATH.read_text(encoding="utf-8"))["RCBO_1P_N"]


def test_rcbo_symbol_has_1p_n_terminals_and_neutral_marking():
    block = rcbo_block()
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 15.24, 270.0, 2.54),
        (0.0, -15.24, 90.0, 2.54),
        (7.62, 15.24, 270.0, 2.54),
        (7.62, -15.24, 90.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4"]
    assert parse_pin_names(block) == ["~", "~", "N", "N"]


def test_rcbo_symbol_matches_approved_reference_structure():
    block = rcbo_block()
    polylines = parse_polylines(block)
    points = {polyline.points for polyline in polylines}
    rectangles = parse_rectangles(block)
    labels = {(item.value, item.x, item.y) for item in parse_texts(block)}

    assert ("T", -17.78, 10.16) in labels
    assert ("E", -18.415, 5.08) in labels
    assert ("1", 1.27, 14.605) in labels
    assert ("3 N", 10.16, 14.605) in labels
    assert ("2", 1.27, -16.51) in labels
    assert ("4 N", 10.16, -16.51) in labels

    assert any(item.dashed for item in polylines)
    assert ((-7.62, 8.255), (24.13, 8.255)) in points

    assert ((-6.35, 10.16), (-5.08, 6.35), (-5.08, -1.27), (0.0, -1.27)) in points
    assert ((-1.27, 10.16), (0.0, 6.35)) in points
    assert ((5.08, 10.16), (7.62, 6.35), (7.62, -12.7)) in points

    assert ((-15.875, 9.525), (-15.875, 12.7), (-5.715, 12.7), (-5.715, 10.16)) in points

    # Links ueber dem Widerstand sitzt der separate offene Testschalter:
    # kurzer fester Kontakt links, beweglicher Hebel schraeg nach rechts unten,
    # danach senkrechter Leiter zum Widerstand.
    assert ((-16.51, 5.08), (-15.875, 5.08)) in points
    assert ((-15.875, 6.35), (-13.335, 3.81), (-13.335, 1.27)) in points

    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (-5.08, -5.08, 12.7, -8.89)
        for item in rectangles
    )
    filled_core = {
        (item.x1, item.y1, item.x2, item.y2)
        for item in rectangles
        if item.filled
    }
    assert (-5.08, -5.08, -2.54, -8.89) in filled_core
    assert (10.16, -5.08, 12.7, -8.89) in filled_core

    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (16.51, 10.16, 21.59, 6.35)
        for item in rectangles
    )
    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (17.78, 3.175, 20.32, -0.635)
        for item in rectangles
    )

    assert ((20.32, 1.27), (22.86, 1.27), (22.86, -10.16), (7.62, -10.16)) in points


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

    assert 'RCBO 1P+N / 2P B16 30mA Typ A 6kA' in block


def test_rcbo_type_a_series_contains_requested_1pn_2p_planning_matrix():
    series = json.loads(TYPE_A_SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    expected = {
        (current, curve, residual, capacity)
        for current in TYPE_A_CURRENTS
        for curve in TYPE_A_CURVES
        for residual in TYPE_A_RESIDUAL_CURRENTS_MA
        for capacity in TYPE_A_BREAKING_CAPACITIES_KA
    }

    assert len(devices) == 64
    assert {
        (
            item["rated_current_a"],
            item["trip_curve"],
            item["residual_current_ma"],
            item["breaking_capacity_ka"],
        )
        for item in devices
    } == expected

    assert {item["rcd_type"] for item in devices} == {"A"}
    assert {item["symbol"] for item in devices} == {"Z_RCBO_1P_N:RCBO_1P_N"}
    assert {item["poles"] for item in devices} == {2}
    assert {item["modules"] for item in devices} == {2}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert "1P+N / 2P" in series["defaults"]["series"]


def test_rcbo_type_a_series_keeps_legacy_baseline_variant_ids():
    series = json.loads(TYPE_A_SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)
    ids = {item["id"] for item in devices}

    for curve in ("b", "c"):
        for current in (6, 10, 16, 20, 25, 32, 40):
            assert (
                f"generic.rcbo-1p-n-type-a-template-series.{curve}{current}"
                in ids
            )


def test_rcbo_type_f_series_is_deliberately_conservative():
    series = json.loads(TYPE_F_SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 2
    assert {
        (
            item["rated_current_a"],
            item["trip_curve"],
            item["residual_current_ma"],
            item["rcd_type"],
            item["breaking_capacity_ka"],
        )
        for item in devices
    } == {
        (6, "C", 30, "F", 6),
        (16, "C", 30, "F", 6),
    }
    assert {item["symbol"] for item in devices} == {"Z_RCBO_1P_N:RCBO_1P_N"}
    assert {item["modules"] for item in devices} == {2}
