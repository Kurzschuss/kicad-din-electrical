from pathlib import Path


RCD_SYMBOL = Path("symbols/Z_RCD.kicad_sym")
RCD_REFERENCE = Path("docs/04_Reference/Z_RCD_REFERENCE.md")


def test_z_rcd_reference_files_exist():
    assert RCD_SYMBOL.is_file()
    assert RCD_REFERENCE.is_file()


def test_z_rcd_is_two_pole_reference_with_four_pins():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    assert '(property "Z_Poles" "2"' in text
    assert text.count("(pin passive line") == 4
    for number in ("1", "2", "3", "4"):
        assert f'(number "{number}"' in text


def test_z_rcd_metadata_matches_reference_scope():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    expected_properties = {
        "Z_Footprint_Policy": "optional",
        "Z_Rated_Current_A": "40",
        "Z_Residual_Current_mA": "30",
        "Z_RCD_Type": "A",
        "Z_Test_Button": "present",
    }
    for name, value in expected_properties.items():
        assert f'(property "{name}" "{value}"' in text


def test_z_rcd_uses_project_prefix_only_for_extensions():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    assert '(symbol "RCD"' in text
    assert 'property "Z_' in text
    assert 'property "Rated_Current_A"' not in text


def test_z_rcd_reference_documents_safety_boundary():
    text = RCD_REFERENCE.read_text(encoding="utf-8")
    assert "ersetzt keine Auswahl" in text
    assert "realen Anlage" in text
