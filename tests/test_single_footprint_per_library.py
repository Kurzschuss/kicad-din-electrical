"""Require populated footprint libraries to contain one matching footprint."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = ROOT / "footprints"


def test_populated_pretty_directories_contain_exactly_one_matching_footprint():
    invalid_libraries = []

    for directory in sorted(
        path
        for path in FOOTPRINT_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(".pretty")
    ):
        footprint_files = sorted(directory.glob("*.kicad_mod"))
        if not footprint_files:
            continue

        library_name = directory.name.removesuffix(".pretty")
        expected_filename = f"{library_name}.kicad_mod"
        actual_filenames = [path.name for path in footprint_files]

        if actual_filenames != [expected_filename]:
            invalid_libraries.append(
                (
                    directory.relative_to(ROOT).as_posix(),
                    expected_filename,
                    actual_filenames,
                )
            )

    assert invalid_libraries == []
