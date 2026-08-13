from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

MODULE_PATH = TOOLS / "apply_qet_de_names.py"
SPEC = importlib.util.spec_from_file_location("apply_qet_de_names_pneumatic", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SOURCE_COMMIT = "42692ea76d2fcc3c6cf1ca335951584cd0978922"
EXPECTED_PATH = "50_pneumatic/5030_actuators/503070_cylinder_special/50307012_cylinder_cable.elmt"
EXPECTED_NAME = "Pneumatischer Seilzugzylinder mit beidseitiger Festdämpfung"


def test_pneumatic_override_set_has_exact_single_audited_path():
    config_dir = ROOT / "config" / "qet_de_names" / "50_pneumatic"
    overrides = mod.load_overrides(config_dir)

    assert overrides == {EXPECTED_PATH: EXPECTED_NAME}


def test_pneumatic_override_file_is_pinned_to_audited_collection():
    config_file = ROOT / "config" / "qet_de_names" / "50_pneumatic" / "all.json"
    payload = json.loads(config_file.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["source_commit"] == SOURCE_COMMIT
    assert payload["scope"] == "50_pneumatic"
    assert payload["overrides"] == {EXPECTED_PATH: EXPECTED_NAME}
