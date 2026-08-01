"""Keep README library examples aligned with the repository contents."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SYMBOL_ROOT = ROOT / "symbols"
FOOTPRINT_ROOT = ROOT / "footprints"

DOCUMENTED_SYMBOL_PATHS = {"symbols/DIN_Electrical_Symbols/"}
DOCUMENTED_FOOTPRINT_PATH = "footprints/"
DOCUMENTED_SYMBOL_FILES = {
    "Z_MCB.kicad_sym",
    "Z_CONTACTOR.kicad_sym",
    "Z_MAIN_SWITCH.kicad_sym",
}
DOCUMENTED_SYMBOL_IDS = {"Z_MCB:MCB"}
DOCUMENTED_FOOTPRINT_FILES = {
    "Z_DIN_Module_18mm.kicad_mod",
    "Z_DIN_Terminal_Block.kicad_mod",
}
DOCUMENTED_FOOTPRINT_IDS = {"Z_DIN_Module_18mm:Z_DIN_Module_18mm"}


def test_readme_library_paths_exist():
    readme = README.read_text(encoding="utf-8")

    for relative_path in DOCUMENTED_SYMBOL_PATHS:
        assert (ROOT / relative_path).is_dir()
        assert f"`{relative_path}`" in readme

    assert (ROOT / DOCUMENTED_FOOTPRINT_PATH).is_dir()
    assert DOCUMENTED_FOOTPRINT_PATH in readme


def test_readme_symbol_examples_exist():
    readme = README.read_text(encoding="utf-8")
    available_files = {path.name for path in SYMBOL_ROOT.rglob("*.kicad_sym")}

    assert DOCUMENTED_SYMBOL_FILES <= available_files
    for filename in DOCUMENTED_SYMBOL_FILES:
        assert f"`{filename}`" in readme

    for symbol_id in DOCUMENTED_SYMBOL_IDS:
        library_name, symbol_name = symbol_id.split(":", 1)
        library_paths = list(SYMBOL_ROOT.rglob(f"{library_name}.kicad_sym"))
        assert len(library_paths) == 1
        content = library_paths[0].read_text(encoding="utf-8")
        assert f'(symbol "{symbol_name}"' in content
        assert symbol_id in readme


def test_readme_footprint_examples_exist():
    readme = README.read_text(encoding="utf-8")
    available_files = {path.name for path in FOOTPRINT_ROOT.rglob("*.kicad_mod")}

    assert DOCUMENTED_FOOTPRINT_FILES <= available_files
    for filename in DOCUMENTED_FOOTPRINT_FILES:
        assert f"`{filename}`" in readme

    for footprint_id in DOCUMENTED_FOOTPRINT_IDS:
        library_name, footprint_name = footprint_id.split(":", 1)
        assert library_name == footprint_name
        assert (FOOTPRINT_ROOT / f"{library_name}.pretty" / f"{footprint_name}.kicad_mod").is_file()
        assert footprint_id in readme
