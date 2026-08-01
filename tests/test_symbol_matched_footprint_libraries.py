"""Keep footprint library folders aligned with symbol library filenames."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
FOOTPRINT_ROOT = ROOT / "footprints"


def test_every_symbol_library_has_matching_pretty_directory():
    symbol_library_names = {
        path.stem
        for path in SYMBOL_ROOT.rglob("*.kicad_sym")
    }
    footprint_library_names = {
        path.name.removesuffix(".pretty")
        for path in FOOTPRINT_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(".pretty")
    }

    missing_directories = sorted(symbol_library_names - footprint_library_names)
    unexpected_directories = sorted(footprint_library_names - symbol_library_names)

    assert missing_directories == []
    assert unexpected_directories == []
