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
    symbol_blocks,
)


CONTACTOR_PATH = Path("symbols/Z_CONTACTOR.kicad_sym")
SERIES_PATH = Path("data/device_series/generic/contactor-3p-ac3-template-series.yaml")
CURRENTS = (9, 12, 18, 25, 32)


def contactor_block() -> str:
    return symbol_blocks(CONTACTOR_PATH.read_text(encoding="utf-8"))["CONTACTOR"]


def test_contactor_symbol_has_three_power_poles_and_coil_terminals():
    block = contactor_block()
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 12.7, 270.0, 2.54),
        (0.0, -12.7, 90.0, 2.54),
        (7.62, 12.7, 270.0, 2.54),
        (7.62, -12.7, 90.0, 2.54),
        (15.24, 12.7, 270.0, 2.54),
        (15.24, -12.7, 90.0, 2.54),
        (17.78, 0.0, 0.0, 2.54),
        (27.94, 0.0, 180.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4", "5", "6", "A1", "A2"]
    assert parse_pin_names(block) == ["L1", "T1", "L2", "T2", "L3", "T3", "A1", "A2"]


def test_contactor_symbol_contains_three_no_contacts_mechanical_coupling_and_coil():
    block = contactor_block()
    polylines = parse_polylines(block)
    points = {polyline.points for polyline in polylines}
    rectangles = parse_rectangles(block)
    labels = {(item.value, item.x, item.y) for item in parse_texts(block)}

    for x in (0.0, 7.62, 15.24):
        assert ((x, 10.16), (x, 8.89)) in points
        assert ((x - 2.54, 8.89), (x, 3.81)) in points
        assert ((x, 3.81), (x, -10.16)) in points

    assert any(item.dashed for item in polylines)
    assert any(
        (item.x1, item.y1, item.x2, item.y2) == (20.32, 2.54, 25.4, -2.54)
        for item in rectangles
    )
    assert ("K", 22.86, 0.0) in labels


def test_contactor_symbol_reference_metadata_is_complete():
    block = contactor_block()
    expected_properties = {
        "Z_Footprint_Policy": "optional",
        "Z_Poles": "3",
        "Z_Main_Contacts": "3NO",
        "Z_Rated_Current_A": "12",
        "Z_Utilization_Category": "AC-3",
        "Z_Coil_Terminals": "A1/A2",
        "Z_Standard": "DIN EN 60947-4-1",
    }
    for name, value in expected_properties.items():
        assert f'(property "{name}" "{value}"' in block


def test_contactor_series_contains_conservative_ac3_planning_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == len(CURRENTS)
    assert {item["rated_current_a"] for item in devices} == set(CURRENTS)
    assert {item["poles"] for item in devices} == {3}
    assert {item["main_contacts_no"] for item in devices} == {3}
    assert {item["main_contacts_nc"] for item in devices} == {0}
    assert {item["utilization_category"] for item in devices} == {"AC-3"}
    assert {item["symbol"] for item in devices} == {"Z_CONTACTOR:CONTACTOR"}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert {item["source_status"] for item in devices} == {"template"}
    assert {item["abbreviation"] for item in devices} == {"K"}
    assert all(item["name_de"] and item["name_en"] for item in devices)


def test_contactor_series_does_not_invent_coil_voltage_or_mechanical_width():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    for item in devices:
        assert "coil_voltage_v" not in item
        assert "coil_voltage_type" not in item
        assert "modules" not in item
        assert "footprint" not in item
