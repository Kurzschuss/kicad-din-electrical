from pathlib import Path

import pytest

from tools.generate_device_variants import expand_series, generated_files


def sample_series() -> dict[str, object]:
    return {
        "series_id": "generic.test-series",
        "defaults": {
            "manufacturer": "Generic",
            "series": "Test",
            "part_number": "BASE",
            "device_type": "Testgerät",
            "function_group": "Test",
            "symbol": "Z_Test:Test",
            "footprint_policy": "optional",
        },
        "variants": [
            {"variant_id": "v1", "part_number": "TEST-1", "rated_current_a": 10},
            {"variant_id": "v2", "part_number": "TEST-2", "rated_current_a": 16},
        ],
    }


def test_expands_defaults_and_variant_values():
    devices = expand_series(sample_series())
    assert [item["id"] for item in devices] == [
        "generic.test-series.v1",
        "generic.test-series.v2",
    ]
    assert devices[0]["manufacturer"] == "Generic"
    assert devices[1]["rated_current_a"] == 16
    assert "variant_id" not in devices[0]


def test_rejects_duplicate_variant_ids():
    data = sample_series()
    data["variants"] = [
        {"variant_id": "v1", "part_number": "A"},
        {"variant_id": "v1", "part_number": "B"},
    ]
    with pytest.raises(ValueError, match="doppelte variant_id"):
        expand_series(data)


def test_generated_files_use_stable_paths(tmp_path: Path):
    series_root = tmp_path / "series"
    output_root = tmp_path / "out"
    series_root.mkdir()
    import json
    (series_root / "test.yaml").write_text(json.dumps(sample_series()), encoding="utf-8")

    files = generated_files(series_root, output_root)

    assert sorted(path.relative_to(output_root).as_posix() for path in files) == [
        "generic.test-series/v1.yaml",
        "generic.test-series/v2.yaml",
    ]
