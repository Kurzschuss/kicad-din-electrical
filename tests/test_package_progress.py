import copy
from pathlib import Path

import pytest

from tools.generate_package_progress import OUTPUT, load_progress, render


def test_committed_progress_overview_is_current():
    assert OUTPUT.read_text(encoding="utf-8") == render(load_progress())


def test_all_package_ids_use_z_prefix():
    payload = load_progress()
    assert all(family["id"].startswith("Z_") for family in payload["families"])


def test_mcb_is_first_checked_reference_package():
    families = {family["id"]: family for family in load_progress()["families"]}
    mcb = families["Z_MCB"]
    assert mcb["quality_status"] == "z_conform"
    assert mcb["quality_level"] == "Geprüft"
    assert mcb["symbol"] and mcb["device_data"] and mcb["documentation"] and mcb["tests"]
    assert not mcb["example"]


def test_checked_package_requires_symbol_data_documentation_tests_and_evidence(tmp_path):
    payload = copy.deepcopy(load_progress())
    package = payload["families"][0]
    package["documentation"] = False
    path = tmp_path / "progress.json"
    import json

    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Checked package is incomplete"):
        load_progress(path)


def test_checked_package_cannot_have_needs_rework_status(tmp_path):
    payload = copy.deepcopy(load_progress())
    payload["families"][0]["quality_status"] = "needs_rework"
    path = tmp_path / "progress.json"
    import json

    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot require rework"):
        load_progress(path)


def test_practice_tested_requires_complete_package(tmp_path):
    payload = copy.deepcopy(load_progress())
    payload["families"][0]["quality_level"] = "Praxisgetestet"
    path = tmp_path / "progress.json"
    import json

    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Praxisgetestet package is incomplete"):
        load_progress(path)


def test_duplicate_package_ids_are_rejected(tmp_path):
    payload = copy.deepcopy(load_progress())
    payload["families"].append(copy.deepcopy(payload["families"][0]))
    path = tmp_path / "progress.json"
    import json

    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate package id"):
        load_progress(path)
