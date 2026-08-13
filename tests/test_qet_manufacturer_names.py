from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("apply_qet_de_names_manufacturers", TOOLS / "apply_qet_de_names.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_manufacturer_override_files_have_unique_scoped_paths():
    config_dir = Path(__file__).resolve().parents[1] / "config" / "qet_de_names" / "manufacturers"
    overrides = mod.load_overrides(config_dir)
    assert overrides
    assert all(path.startswith("10_electric/20_manufacturers_articles/") for path in overrides)
    assert all(name.strip() for name in overrides.values())
