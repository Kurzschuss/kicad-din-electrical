from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "apply_qet_de_names.py"
SPEC = importlib.util.spec_from_file_location("apply_qet_de_names", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def sample_symbol(path: str, value: str, adjustment: str = "none") -> str:
    return f'''  (symbol "Z_Q_test"
    (property "Reference" "QET" (at 0 0 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at 0 0 0) (effects (font (size 1.27 1.27))))
    (property "Description" "{value} | QET-Kategorie: 10_electric / 10_allpole / test" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "QET_Category" "10_electric / 10_allpole / test" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "QET_Source_Path" "{path}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "QET_Adjustments" "{adjustment}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "ki_keywords" "{value} test" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "Z_Q_test_0_1")
  )'''


def test_finalize_applies_only_configured_path():
    target = "10_electric/10_allpole/test/english.elmt"
    library = "(kicad_symbol_lib (version 20231120) (generator qet_to_kicad)\n" + sample_symbol(target, "English") + "\n)\n"

    finalized, report = mod.finalize_library(library, {target: "Deutsch"})

    assert '(property "Value" "Deutsch"' in finalized
    assert 'Deutsch | QET-Kategorie: 10_electric / 10_allpole / test' in finalized
    assert 'german_name_override' in finalized
    assert 'Deutsch English English test' in finalized
    assert report["configured_overrides"] == 1
    assert report["applied_overrides"] == 1
    assert report["unmatched_override_paths"] == []


def test_finalize_removes_stale_german_fallback_but_keeps_other_adjustments():
    target = "10_electric/10_allpole/test/english.elmt"
    library = (
        "(kicad_symbol_lib (version 20231120) (generator qet_to_kicad)\n"
        + sample_symbol(
            target,
            "English",
            "arc_approximated; german_name_fallback:en; generated_pin_number",
        )
        + "\n)\n"
    )

    finalized, report = mod.finalize_library(library, {target: "Deutsch"})

    assert "german_name_fallback:" not in finalized
    assert (
        '(property "QET_Adjustments" '
        '"arc_approximated; generated_pin_number; german_name_override"'
    ) in finalized
    assert report["applied_overrides"] == 1


def test_unmatched_override_is_reported():
    library = "(kicad_symbol_lib (version 20231120) (generator qet_to_kicad)\n)\n"
    _, report = mod.finalize_library(library, {"10_electric/10_allpole/test/missing.elmt": "Deutsch"})
    assert report["applied_overrides"] == 0
    assert report["unmatched_override_paths"] == ["10_electric/10_allpole/test/missing.elmt"]


def test_duplicate_override_paths_are_rejected(tmp_path: Path):
    config = tmp_path / "names"
    config.mkdir()
    payload = {"schema_version": 1, "overrides": {"10_electric/a.elmt": "A"}}
    (config / "a.json").write_text(json.dumps(payload), encoding="utf-8")
    (config / "b.json").write_text(json.dumps(payload), encoding="utf-8")

    try:
        mod.load_overrides(config)
    except ValueError as exc:
        assert "Duplicate German override" in str(exc)
    else:
        raise AssertionError("duplicate override was accepted")


def test_phase1_override_set_has_184_unique_paths():
    config_dir = Path(__file__).resolve().parents[1] / "config" / "qet_de_names" / "10_allpole"
    overrides = mod.load_overrides(config_dir)
    assert len(overrides) == 184
    assert all(path.startswith("10_electric/10_allpole/") for path in overrides)
    assert all(name.strip() for name in overrides.values())
