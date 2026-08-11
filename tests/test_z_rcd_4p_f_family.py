import json
from pathlib import Path

from tools.generate_device_variants import expand_series


SERIES_PATH = Path("data/device_series/generic/rcd-4p-f-template-series.yaml")
CURRENTS = (25, 40, 63)
RESIDUAL_CURRENTS = (30, 300, 500)


def test_rcd_4p_f_series_contains_conservative_variant_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 9
    assert {
        (
            item["rated_current_a"],
            item["residual_current_ma"],
            item["rcd_type"],
        )
        for item in devices
    } == {
        (current, residual, "F")
        for current in CURRENTS
        for residual in RESIDUAL_CURRENTS
    }


def test_rcd_4p_f_series_reuses_approved_symbol_without_invented_short_circuit_values():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert {item["symbol"] for item in devices} == {"Z_RCD:RCD_4P"}
    assert {item["poles"] for item in devices} == {4}
    assert {item["modules"] for item in devices} == {4}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert {item["source_status"] for item in devices} == {"template"}

    for item in devices:
        assert "rated_short_circuit_current_ka" not in item
        assert "making_breaking_capacity_ka" not in item
