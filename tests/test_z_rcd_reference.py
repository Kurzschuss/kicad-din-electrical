from pathlib import Path


RCD_SYMBOL = Path("symbols/Z_RCD.kicad_sym")
RCD_REFERENCE = Path("docs/04_Reference/Z_RCD_REFERENCE.md")
RCD_FOOTPRINT_2P = Path("footprints/Z_RCD.pretty/Z_RCD_2P_36mm.kicad_mod")
RCD_FOOTPRINT_4P = Path("footprints/Z_RCD.pretty/Z_RCD_4P_72mm.kicad_mod")


def _symbol_section(text: str, name: str, next_name: str | None = None) -> str:
    start = text.index(f'  (symbol "{name}"')
    if next_name is None:
        return text[start:]
    end = text.index(f'  (symbol "{next_name}"', start)
    return text[start:end]


def test_z_rcd_reference_files_exist():
    assert RCD_SYMBOL.is_file()
    assert RCD_REFERENCE.is_file()
    assert RCD_FOOTPRINT_2P.is_file()
    assert RCD_FOOTPRINT_4P.is_file()


def test_z_rcd_family_has_two_and_four_pole_variants():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    two = _symbol_section(text, "RCD_2P", "RCD_4P")
    four = _symbol_section(text, "RCD_4P")

    assert '(property "Z_Poles" "2"' in two
    assert two.count("(pin passive line") == 4
    for number in ("1", "2", "3", "4"):
        assert f'(number "{number}"' in two

    assert '(property "Z_Poles" "4"' in four
    assert four.count("(pin passive line") == 8
    for number in ("1", "2", "3", "4", "5", "6", "7", "8"):
        assert f'(number "{number}"' in four


def test_z_rcd_metadata_matches_current_family_scope():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    for name in ("RCD_2P", "RCD_4P"):
        next_name = "RCD_4P" if name == "RCD_2P" else None
        section = _symbol_section(text, name, next_name)
        assert '(property "Z_Footprint_Policy" "optional"' in section
        assert '(property "Z_Test_Button" "present"' in section
        assert '(property "Manufacturer" ""' in section
        assert '(property "Part Number" ""' in section


def test_z_rcd_uses_project_prefix_only_for_extensions():
    text = RCD_SYMBOL.read_text(encoding="utf-8")
    assert '(symbol "RCD_2P"' in text
    assert '(symbol "RCD_4P"' in text
    assert 'property "Z_' in text
    assert 'property "Rated_Current_A"' not in text


def test_z_rcd_variants_bind_to_projectos_footprints():
    symbol = RCD_SYMBOL.read_text(encoding="utf-8")
    footprint_2p = RCD_FOOTPRINT_2P.read_text(encoding="utf-8")
    footprint_4p = RCD_FOOTPRINT_4P.read_text(encoding="utf-8")

    assert '(property "Footprint" "Z_RCD:Z_RCD_2P_36mm"' in symbol
    assert '(property "Footprint" "Z_RCD:Z_RCD_4P_72mm"' in symbol
    assert '(start -18 -52)' in footprint_2p
    assert '(end 18 52)' in footprint_2p
    assert '(start -36 -52)' in footprint_4p
    assert '(end 36 52)' in footprint_4p
    assert footprint_2p.count('(drill 4)') == 4
    assert footprint_4p.count('(drill 4)') == 8


def test_z_rcd_reference_documents_safety_boundary():
    text = RCD_REFERENCE.read_text(encoding="utf-8")
    assert "ersetzt keine Auswahl" in text
    assert "realen Anlage" in text
    assert "keine Bohr-, Anschluss- oder Fertigungsfreigabe" in text
