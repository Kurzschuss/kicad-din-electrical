from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    "apply_qet_language_neutral_names", TOOLS / "apply_qet_language_neutral_names.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def item(path: str, **names):
    return {"path": path, "names": names}


def test_model_identifier_is_accepted_when_multilingual_majority_agrees():
    candidate = mod.language_neutral_candidate(
        item("x.elmt", en="6ES7 132-6BH01-0BA0 DQ ST 16X24VDC", fr="6ES7 132-6BH01-0BA0 DQ ST 16X24VDC", ca="6ES7 132-6BH01-0BA0 DQ ST 16X24VDC")
    )
    assert candidate == "6ES7 132-6BH01-0BA0 DQ ST 16X24VDC"


def test_common_english_function_word_blocks_auto_acceptance():
    assert mod.language_neutral_candidate(
        item("x.elmt", en="SPDT on-off-on", fr="SPDT on-off-on", ca="SPDT on-off-on")
    ) is None
    assert mod.language_neutral_candidate(
        item("x.elmt", en="Safety relay 2", fr="Safety relay 2", ca="Safety relay 2")
    ) is None


def test_generic_translatable_name_is_not_accepted():
    assert mod.language_neutral_candidate(
        item("x.elmt", en="Temperature sensor", fr="Capteur de temperature", ca="Sensor de temperatura")
    ) is None


def test_finalization_marks_accepted_model_and_removes_fallback():
    path = "10_electric/20_manufacturers_articles/vendor/model.elmt"
    library = f'''(kicad_symbol_lib (version 20231120) (generator qet_to_kicad)
  (symbol "Z_Q_model"
    (property "Reference" "QET" (at 0 0 0) (effects (font (size 1 1))))
    (property "Value" "MODEL-24VDC" (at 0 0 0) (effects (font (size 1 1))))
    (property "Description" "MODEL-24VDC | QET-Kategorie: 10_electric / 20_manufacturers_articles / vendor" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
    (property "QET_Category" "10_electric / 20_manufacturers_articles / vendor" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
    (property "QET_Source_Path" "{path}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
    (property "QET_Adjustments" "german_name_fallback:en; reference_prefix_missing:qet_placeholder" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
    (property "ki_keywords" "MODEL-24VDC" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
    (symbol "Z_Q_model_0_1")
  )
)
'''
    audit = {"items": [item(path, en="MODEL-24VDC", fr="MODEL-24VDC", ca="MODEL-24VDC")]}
    finalized, report = mod.finalize_library(library, audit)
    assert report["language_neutral_applied"] == 1
    assert report["remaining_translation_count"] == 0
    assert "language_neutral_name_accepted" in finalized
    assert "german_name_fallback:en" not in finalized
