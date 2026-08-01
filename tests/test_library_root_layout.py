"""Enforce the repository root layout for KiCad symbol and footprint files."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
SYMBOL_LIBRARY_ROOT = SYMBOL_ROOT / "DIN_Electrical_Symbols"
FOOTPRINT_ROOT = ROOT / "footprints"


def test_symbol_files_are_only_in_din_electrical_symbols_directory():
    misplaced = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(SYMBOL_ROOT.rglob("*.kicad_sym"))
        if path.parent != SYMBOL_LIBRARY_ROOT
    ]

    assert misplaced == []


def test_footprint_files_are_not_stored_directly_under_footprints_root():
    misplaced = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(FOOTPRINT_ROOT.glob("*.kicad_mod"))
    ]

    assert misplaced == []
