import json
from pathlib import Path


MCB = Path("symbols/Z_MCB.kicad_sym")
PREVIEW = Path("docs/site/symbol-previews/Z_MCB/MCB.svg")
MANIFEST = Path("projects/Z_MCB_reference/Z_PROJECT_MANIFEST.json")


def _mcb_1p_symbol_text() -> str:
    content = MCB.read_text(encoding="utf-8")
    return content.split('\n  (symbol "MCB_3P"', 1)[0]


def test_mcb_1p_pin_contract_is_exactly_two_passive_pins() -> None:
    content = _mcb_1p_symbol_text()

    assert content.count("(pin passive line") == 2
    assert '(number "1"' in content
    assert '(number "2"' in content
    assert '(name "1"' in content
    assert '(name "2"' in content


def test_mcb_1p_has_visible_switch_protection_graphic() -> None:
    content = _mcb_1p_symbol_text()

    assert content.count("(polyline") >= 2
    assert '(xy -2.54 0)' in content
    assert '(xy 1.27 -1.27)' in content
    assert '(xy 0.76 1.27)' in content


def test_mcb_1p_remains_manufacturer_neutral() -> None:
    content = _mcb_1p_symbol_text()

    assert '(property "Manufacturer" ""' in content
    assert '(property "Part Number" ""' in content
    assert '(property "Z_Footprint_Policy" "optional"' in content
    assert 'B16' not in content


def test_mcb_preview_contains_goldstandard_function_graphic() -> None:
    content = PREVIEW.read_text(encoding="utf-8")

    assert "<title>Z_MCB: MCB</title>" in content
    assert content.count("<polyline") >= 2
    assert 'points="89.52,90.00 104.76,90.00 135.24,105.24 150.48,105.24"' in content


def test_mcb_reference_stays_draft_until_real_kicad_validation() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["quality_level"] == "Entwurf"
    assert manifest["validation"]["symbol_placed"] is False
    assert manifest["validation"]["erc_checked"] is False
    assert manifest["validation"]["opened_in_kicad"] is False
