from pathlib import Path


MCB = Path("symbols/Z_MCB.kicad_sym")


def test_mcb_1p_pin_contract_is_exactly_two_passive_pins() -> None:
    content = MCB.read_text(encoding="utf-8")

    assert content.count("(pin passive line") == 2
    assert '(number "1"' in content
    assert '(number "2"' in content
    assert '(name "1"' in content
    assert '(name "2"' in content


def test_mcb_1p_has_visible_switch_protection_graphic() -> None:
    content = MCB.read_text(encoding="utf-8")

    assert content.count("(polyline") >= 2
    assert '(xy -2.54 0)' in content
    assert '(xy 1.27 -1.27)' in content
    assert '(xy 0.76 1.27)' in content


def test_mcb_1p_remains_manufacturer_neutral() -> None:
    content = MCB.read_text(encoding="utf-8")

    assert '(property "Manufacturer" ""' in content
    assert '(property "Part Number" ""' in content
    assert '(property "Z_Footprint_Policy" "optional"' in content
    assert 'B16' not in content
