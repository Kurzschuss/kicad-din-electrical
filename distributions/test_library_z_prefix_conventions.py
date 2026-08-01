"""Regression tests for the repository-wide Z_ library naming convention."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
FOOTPRINT_ROOT = ROOT / "footprints"
REFERENCE_ROOTS = (
    ROOT / "metadata",
    ROOT / "tools",
    ROOT / "projects",
)
REFERENCE_SUFFIXES = {
    ".csv",
    ".json",
    ".kicad_pcb",
    ".kicad_pro",
    ".kicad_sch",
    ".yaml",
    ".yml",
}
FOOTPRINT_NAME_PATTERN = r"DIN_(?:Module_(?:18|36|45)mm|Contactor_45mm|Safety_Module|Terminal_Block)"
OLD_FOOTPRINT_RE = re.compile(rf"(?<!Z_){FOOTPRINT_NAME_PATTERN}")
PREFIXED_FOOTPRINT_RE = re.compile(rf"\bZ_{FOOTPRINT_NAME_PATTERN}\b")
PREFIXED_SYMBOL_ID_RE = re.compile(r"\b(Z_[A-Za-z0-9_]+):([A-Za-z0-9_]+)\b")
TOP_LEVEL_SYMBOL_RE = re.compile(r'^  \(symbol "([^"]+)"', re.MULTILINE)


def _machine_readable_reference_files() -> list[Path]:
    return sorted(
        path
        for root in REFERENCE_ROOTS
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in REFERENCE_SUFFIXES
    )


def _duplicate_stems(paths: list[Path], *, case_sensitive: bool = True) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for path in paths:
        key = path.stem if case_sensitive else path.stem.casefold()
        grouped.setdefault(key, []).append(path.relative_to(ROOT).as_posix())
    return {name: locations for name, locations in grouped.items() if len(locations) > 1}


def test_all_symbol_library_files_use_z_prefix():
    symbol_files = sorted(SYMBOL_ROOT.rglob("*.kicad_sym"))
    assert symbol_files, "No KiCad symbol libraries found"

    unprefixed = [path.relative_to(ROOT).as_posix() for path in symbol_files if not path.name.startswith("Z_")]
    assert unprefixed == []


def test_symbol_library_names_are_unique_repository_wide():
    symbol_files = sorted(SYMBOL_ROOT.rglob("*.kicad_sym"))
    assert _duplicate_stems(symbol_files) == {}


def test_symbol_library_names_are_unique_case_insensitively():
    symbol_files = sorted(SYMBOL_ROOT.rglob("*.kicad_sym"))
    assert _duplicate_stems(symbol_files, case_sensitive=False) == {}


def test_single_symbol_library_files_match_primary_symbol_names():
    mismatches = []
    for path in sorted(SYMBOL_ROOT.rglob("*.kicad_sym")):
        top_level_symbols = TOP_LEVEL_SYMBOL_RE.findall(path.read_text(encoding="utf-8"))
        if len(top_level_symbols) != 1:
            continue

        expected_symbol = path.stem.removeprefix("Z_")
        actual_symbol = top_level_symbols[0]
        if actual_symbol != expected_symbol:
            mismatches.append((path.relative_to(ROOT).as_posix(), expected_symbol, actual_symbol))

    assert mismatches == []


def test_all_footprint_files_and_library_directories_use_z_prefix():
    footprint_files = sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod"))
    assert footprint_files, "No KiCad footprints found"

    unprefixed_files = [
        path.relative_to(ROOT).as_posix() for path in footprint_files if not path.name.startswith("Z_")
    ]
    unprefixed_libraries = sorted(
        {
            path.parent.relative_to(ROOT).as_posix()
            for path in footprint_files
            if path.parent != FOOTPRINT_ROOT and not path.parent.name.startswith("Z_")
        }
    )
    assert unprefixed_files == []
    assert unprefixed_libraries == []


def test_footprint_names_are_unique_repository_wide():
    footprint_files = sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod"))
    assert _duplicate_stems(footprint_files) == {}


def test_footprint_names_are_unique_case_insensitively():
    footprint_files = sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod"))
    assert _duplicate_stems(footprint_files, case_sensitive=False) == {}


def test_internal_footprint_names_match_prefixed_filenames():
    mismatches = []
    for path in sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod")):
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        expected = f'(footprint "{path.stem}"'
        if not first_line.startswith(expected):
            mismatches.append(path.relative_to(ROOT).as_posix())

    assert mismatches == []


def test_machine_readable_references_do_not_use_old_footprint_names():
    reference_files = _machine_readable_reference_files()
    assert reference_files, "No machine-readable footprint reference files found"

    stale_references = []
    for path in reference_files:
        content = path.read_text(encoding="utf-8")
        if OLD_FOOTPRINT_RE.search(content):
            stale_references.append(path.relative_to(ROOT).as_posix())

    assert stale_references == []


def test_machine_readable_footprint_references_target_existing_files():
    reference_files = _machine_readable_reference_files()
    assert reference_files, "No machine-readable footprint reference files found"

    available_footprints = {path.stem for path in FOOTPRINT_ROOT.rglob("*.kicad_mod")}
    missing_targets = []
    for path in reference_files:
        content = path.read_text(encoding="utf-8")
        for footprint_name in sorted(set(PREFIXED_FOOTPRINT_RE.findall(content))):
            if footprint_name not in available_footprints:
                missing_targets.append((path.relative_to(ROOT).as_posix(), footprint_name))

    assert missing_targets == []


def test_machine_readable_symbol_ids_target_existing_symbols():
    reference_files = _machine_readable_reference_files()
    assert reference_files, "No machine-readable symbol reference files found"

    library_files = {path.stem: path for path in SYMBOL_ROOT.rglob("*.kicad_sym")}
    library_contents = {
        library_name: path.read_text(encoding="utf-8")
        for library_name, path in library_files.items()
    }
    missing_targets = []
    for path in reference_files:
        content = path.read_text(encoding="utf-8")
        for library_name, symbol_name in sorted(set(PREFIXED_SYMBOL_ID_RE.findall(content))):
            symbol_id = f"{library_name}:{symbol_name}"
            if library_name not in library_files:
                missing_targets.append((path.relative_to(ROOT).as_posix(), symbol_id, "library"))
                continue

            symbol_declaration = f'(symbol "{symbol_name}"'
            if symbol_declaration not in library_contents[library_name]:
                missing_targets.append((path.relative_to(ROOT).as_posix(), symbol_id, "symbol"))

    assert missing_targets == []
