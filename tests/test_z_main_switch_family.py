import json
from pathlib import Path

from tools.generate_device_variants import expand_series
from tools.generate_symbol_previews import (
    parse_pin_names,
    parse_pin_numbers,
    parse_pins,
    parse_polylines,
    symbol_blocks,
)


SYMBOL_PATH = Path("symbols/Z_MAIN_SWITCH.kicad_sym")
SERIES_2P_PATH = Path("data/device_series/generic/main-switch-2p-template-series.yaml")
SERIES_4P_PATH = Path("data/device_series/generic/main-switch-4p-template-series.yaml")
RATED_CURRENTS = {16, 25, 40, 63}


def blocks() -> dict[str, str]:
    return symbol_blocks(SYMBOL_PATH.read_text(encoding="utf-8"))


def test_main_switch_library_contains_2p_and_4p_symbols():
    assert set(blocks()) == {"MAIN_SWITCH", "MAIN_SWITCH_4P"}


def test_main_switch_2p_has_l_n_terminals_and_mechanical_coupling():
    block = blocks()["MAIN_SWITCH"]
    pins = parse_pins(block)

    assert [(pin.x, pin.y, pin.angle, pin.length) for pin in pins] == [
        (0.0, 12.7, 270.0, 2.54),
        (0.0, -12.7, 90.0, 2.54),
        (7.62, 12.7, 270.0, 2.54),
        (7.62, -12.7, 90.0, 2.54),
    ]
    assert parse_pin_numbers(block) == ["1", "2", "3", "4"]
    assert parse_pin_names(block) == ["~", "~", "N", "N"]
    assert sum(item.dashed for item in parse_polylines(block)) == 1


def test_main_switch_4p_has_3p_n_terminals_and_mechanical_coupling():
    block = blocks()["MAIN_SWITCH_4P"]
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
    assert sum(item.dashed for item in parse_polylines(block)) == 1


def test_main_switch_symbols_use_function_geometry_instead_of_placeholder_box():
    for name, pole_positions in {
        "MAIN_SWITCH": (0.0, 7.62),
        "MAIN_SWITCH_4P": (0.0, 7.62, 15.24, 22.86),
    }.items():
        block = blocks()[name]
        points = {polyline.points for polyline in parse_polylines(block)}
        assert '(text "HS"' not in block
        assert "(rectangle " not in block
        for x in pole_positions:
            assert ((x, 10.16), (x, 8.89)) in points
            assert ((x - 2.54, 8.89), (x, 3.81)) in points
            assert ((x, 3.81), (x, -10.16)) in points


def test_main_switch_symbol_metadata_is_complete():
    expected = {
        "MAIN_SWITCH": {"Z_Poles": "2", "Z_Rated_Current_A": "40"},
        "MAIN_SWITCH_4P": {"Z_Poles": "4", "Z_Rated_Current_A": "40"},
    }
    for name, specific in expected.items():
        block = blocks()[name]
        common = {
            "Z_Footprint_Policy": "optional",
            "Z_Switch_Function": "main_switch",
            "Z_Standard": "DIN EN 60947-3",
        }
        for key, value in {**common, **specific}.items():
            assert f'(property "{key}" "{value}"' in block


def _devices(path: Path) -> list[dict]:
    return expand_series(json.loads(path.read_text(encoding="utf-8")))


def test_main_switch_2p_series_contains_neutral_planning_matrix():
    devices = _devices(SERIES_2P_PATH)
    assert len(devices) == 4
    assert {item["rated_current_a"] for item in devices} == RATED_CURRENTS
    assert {item["poles"] for item in devices} == {2}
    assert {item["modules"] for item in devices} == {2}
    assert {item["symbol"] for item in devices} == {"Z_MAIN_SWITCH:MAIN_SWITCH"}
    assert {item["function_group"] for item in devices} == {"switching.main_switch"}
    assert {item["source_status"] for item in devices} == {"template"}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert {item["abbreviation"] for item in devices} == {"HS"}
    assert all(item["name_de"] and item["name_en"] for item in devices)


def test_main_switch_4p_series_contains_neutral_planning_matrix():
    devices = _devices(SERIES_4P_PATH)
    assert len(devices) == 4
    assert {item["rated_current_a"] for item in devices} == RATED_CURRENTS
    assert {item["poles"] for item in devices} == {4}
    assert {item["modules"] for item in devices} == {4}
    assert {item["symbol"] for item in devices} == {"Z_MAIN_SWITCH:MAIN_SWITCH_4P"}
    assert {item["function_group"] for item in devices} == {"switching.main_switch"}
    assert {item["source_status"] for item in devices} == {"template"}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert {item["abbreviation"] for item in devices} == {"HS"}
    assert all(item["name_de"] and item["name_en"] for item in devices)
