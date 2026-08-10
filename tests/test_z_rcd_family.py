import json
from pathlib import Path

from tools.generate_device_variants import expand_series
from tools.generate_symbol_previews import parse_pins, parse_polylines, symbol_blocks


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
        (0.0, 10.16, 270.0, 2.54),
        (0.0, -10.16, 90.0, 2.54),
        (7.62, 10.16, 270.0, 2.54),
        (7.62, -10.16, 90.0, 2.54),
    ]
    for number in ("1", "2", "3", "4"):
        assert f'(number "{number}"' in block
    assert '(name "N"' in block


def test_rcd_symbol_contains_switches_test_circuit_and_residual_trip_function():
    block = symbol_blocks(RCD_PATH.read_text(encoding="utf-8"))["RCD"]
    points = {polyline.points for polyline in parse_polylines(block)}

    assert ((0.0, 7.62), (0.0, 6.35)) in points
    assert ((-2.54, 5.08), (0.0, 1.27)) in points
    assert ((7.62, 7.62), (7.62, 6.35)) in points
    assert ((5.08, 5.08), (7.62, 1.27)) in points
    assert ((-3.81, 2.54), (10.16, 2.54)) in points
    assert '(type dash)' in block
    assert ((-13.97, 6.35), (-11.43, 6.35)) in points
    assert ((-12.7, 6.35), (-12.7, 3.81)) in points
    assert ((13.97, -2.54), (15.24, 0.0), (15.24, -2.54), (13.97, -2.54)) in points
    assert ((16.51, 0.0), (17.78, -1.27), (16.51, -2.54)) in points


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
