from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

MODULE_PATH = TOOLS / "apply_qet_de_names.py"
SPEC = importlib.util.spec_from_file_location("apply_qet_de_names_hydraulic", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SOURCE_COMMIT = "42692ea76d2fcc3c6cf1ca335951584cd0978922"
EXPECTED_COUNTS = {
    "21_tanks": 2,
    "31_control_valves": 60,
    "45_valves": 11,
    "51_cylinders": 8,
    "61_pumps": 11,
    "71_exchangers": 1,
    "81_filters": 1,
}


def test_hydraulic_override_set_has_exact_94_unique_paths():
    config_dir = ROOT / "config" / "qet_de_names" / "30_hydraulic"
    overrides = mod.load_overrides(config_dir)

    assert len(overrides) == 94
    assert all(path.startswith("30_hydraulic/") for path in overrides)
    assert all(path.endswith(".elmt") for path in overrides)
    assert all(name.strip() for name in overrides.values())

    counts = Counter(path.split("/")[1] for path in overrides)
    assert dict(counts) == EXPECTED_COUNTS


def test_hydraulic_override_file_is_pinned_to_audited_collection():
    config_file = ROOT / "config" / "qet_de_names" / "30_hydraulic" / "all.json"
    payload = json.loads(config_file.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["source_commit"] == SOURCE_COMMIT
    assert payload["scope"] == "30_hydraulic"
    assert len(payload["overrides"]) == 94
    assert all(path.startswith("30_hydraulic/") for path in payload["overrides"])
