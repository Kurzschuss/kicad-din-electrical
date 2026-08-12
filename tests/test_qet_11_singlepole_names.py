from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "apply_qet_de_names.py"
SPEC = importlib.util.spec_from_file_location("apply_qet_de_names_11", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_11_singlepole_override_set_has_144_unique_paths():
    config_dir = Path(__file__).resolve().parents[1] / "config" / "qet_de_names" / "11_singlepole"
    overrides = mod.load_overrides(config_dir)
    assert len(overrides) == 144
    assert all(path.startswith("10_electric/11_singlepole/") for path in overrides)
    assert all(name.strip() for name in overrides.values())
