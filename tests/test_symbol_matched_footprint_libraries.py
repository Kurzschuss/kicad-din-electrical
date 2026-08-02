"""Keep footprint library folders aligned with symbols and contained footprints."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
FOOTPRINT_ROOT = ROOT / "footprints"


def test_every_symbol_library_has_matching_pretty_directory():
    symbol_library_names = {path.stem for path in SYMBOL_ROOT.rglob("*.kicad_sym")}
    footprint_library_names = {
        path.name.removesuffix(".pretty")
        for path in FOOTPRINT_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(".pretty")
    }

    assert sorted(symbol_library_names - footprint_library_names) == []


def test_every_footprint_is_directly_inside_a_pretty_directory():
    mismatches = []
    for path in sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod")):
        if not path.parent.name.endswith(".pretty"):
            mismatches.append(path.relative_to(ROOT).as_posix())

    assert mismatches == []


def test_every_pretty_directory_matches_a_symbol_or_contains_footprints():
    symbol_library_names = {path.stem for path in SYMBOL_ROOT.rglob("*.kicad_sym")}
    unexpected = []

    for directory in sorted(
        path
        for path in FOOTPRINT_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(".pretty")
    ):
        library_name = directory.name.removesuffix(".pretty")
        contained_footprints = list(directory.glob("*.kicad_mod"))
        if library_name not in symbol_library_names and not contained_footprints:
            unexpected.append(directory.relative_to(ROOT).as_posix())

    assert unexpected == []
