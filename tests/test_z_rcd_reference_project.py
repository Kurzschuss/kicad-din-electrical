from pathlib import Path


PROJECT = Path("examples/Z_RCD_Reference")
SCHEMATIC = PROJECT / "Z_RCD_Reference.sch"
README = PROJECT / "README.md"
SYMBOL_TABLE = PROJECT / "sym-lib-table"
FOOTPRINT_TABLE = PROJECT / "fp-lib-table"


def test_z_rcd_reference_project_files_exist():
    assert (PROJECT / "Z_RCD_Reference.pro").is_file()
    assert SCHEMATIC.is_file()
    assert README.is_file()
    assert SYMBOL_TABLE.is_file()
    assert FOOTPRINT_TABLE.is_file()


def test_z_rcd_reference_project_uses_only_z_libraries():
    symbols = SYMBOL_TABLE.read_text(encoding="utf-8")
    footprints = FOOTPRINT_TABLE.read_text(encoding="utf-8")

    assert '(name "Z_RCD")' in symbols
    assert "${KICAD_Z_SYMBOL_DIR}/Z_RCD.kicad_sym" in symbols
    assert '(name "Z_DIN_Module_36mm")' in footprints
    assert "${KICAD_Z_FOOTPRINT_DIR}/Z_DIN_Module_36mm.pretty" in footprints


def test_z_rcd_reference_project_places_symbol_and_footprint():
    schematic = SCHEMATIC.read_text(encoding="utf-8")

    assert "EESchema Schematic File Version 4" in schematic
    assert "L Z_RCD:RCD Q1" in schematic
    assert 'F 0 "Q1"' in schematic
    assert 'F 2 "Z_DIN_Module_36mm:Z_DIN_Module_36mm"' in schematic
    for label in ("L_IN", "L_OUT", "N_IN", "N_OUT"):
        assert label in schematic
    assert schematic.count("NoConn ~") == 4


def test_z_rcd_reference_project_documents_real_erc_boundary():
    readme = README.read_text(encoding="utf-8")

    assert "Elektrische Regeln prüfen" in readme
    assert "Praxisgetestet" in readme
    assert "Geprüft" in readme
    assert "automatisierten Tests" in readme
