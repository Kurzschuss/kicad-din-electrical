import json
from pathlib import Path

from tools.generate_device_variants import expand_series


SERIES_PATH = Path("data/device_series/generic/rcd-2p-b-bplus-template-series.yaml")
CURRENTS = (16, 25, 40, 63)
RESIDUAL_CURRENTS = (30, 300)
RCD_TYPES = ("B", "B+")


def test_rcd_2p_b_bplus_series_contains_conservative_variant_matrix():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert len(devices) == 16
    assert {
        (
            item["rated_current_a"],
            item["residual_current_ma"],
            item["rcd_type"],
        )
        for item in devices
    } == {
        (current, residual, rcd_type)
        for current in CURRENTS
        for residual in RESIDUAL_CURRENTS
        for rcd_type in RCD_TYPES
    }


def test_rcd_2p_b_bplus_series_reuses_approved_symbol_without_invented_short_circuit_values():
    series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
    devices = expand_series(series)

    assert {item["symbol"] for item in devices} == {"Z_RCD:RCD"}
    assert {item["poles"] for item in devices} == {2}
    assert {item["modules"] for item in devices} == {2}
    assert {item["footprint_policy"] for item in devices} == {"optional"}
    assert {item["source_status"] for item in devices} == {"template"}

    for item in devices:
        assert "rated_short_circuit_current_ka" not in item
        assert "making_breaking_capacity_ka" not in item
