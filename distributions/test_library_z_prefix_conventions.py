"""Regression tests for the repository-wide Z_ library naming convention."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = ROOT / "symbols"
FOOTPRINT_ROOT = ROOT / "footprints"
REFERENCE_FILES = (
    ROOT / "metadata" / "footprint_mapping.csv",
    ROOT / "metadata" / "component_database.csv",
    ROOT / "metadata" / "abb_products.csv",
    ROOT / "tools" / "bom_template.csv",
    ROOT / "tools" / "component_rules.yaml",
    ROOT / "projects" / "control_cabinet_basic" / "bom.csv",
)
OLD_FOOTPRINT_RE = re.compile(
    r"(?<!Z_)DIN_(?:Module_(?:18|36|45)mm|Contactor_45mm|Safety_Module|Terminal_Block)"
)


def test_all_symbol_library_files_use_z_prefix():
    symbol_files = sorted(SYMBOL_ROOT.rglob("*.kicad_sym"))
    assert symbol_files, "No KiCad symbol libraries found"

    unprefixed = [path.relative_to(ROOT).as_posix() for path in symbol_files if not path.name.startswith("Z_")]
    assert unprefixed == []


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
            if not path.parent.name.startswith("Z_")
        }
    )
    assert unprefixed_files == []
    assert unprefixed_libraries == []


def test_internal_footprint_names_match_prefixed_filenames():
    mismatches = []
    for path in sorted(FOOTPRINT_ROOT.rglob("*.kicad_mod")):
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        expected = f'(footprint "{path.stem}"'
        if not first_line.startswith(expected):
            mismatches.append(path.relative_to(ROOT).as_posix())

    assert mismatches == []


def test_known_metadata_references_do_not_use_old_footprint_names():
    stale_references = []
    for path in REFERENCE_FILES:
        content = path.read_text(encoding="utf-8")
        if OLD_FOOTPRINT_RE.search(content):
            stale_references.append(path.relative_to(ROOT).as_posix())

    assert stale_references == []
