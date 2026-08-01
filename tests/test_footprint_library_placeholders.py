"""Keep .gitkeep files limited to otherwise empty footprint libraries."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = ROOT / "footprints"


def test_gitkeep_files_exist_only_in_empty_pretty_directories():
    invalid_placeholders = []

    for placeholder in sorted(FOOTPRINT_ROOT.rglob(".gitkeep")):
        directory = placeholder.parent
        if not directory.name.endswith(".pretty"):
            invalid_placeholders.append(
                (placeholder.relative_to(ROOT).as_posix(), "outside-pretty-directory")
            )
            continue

        real_files = [
            path
            for path in directory.iterdir()
            if path.is_file() and path.name != ".gitkeep"
        ]
        if real_files:
            invalid_placeholders.append(
                (
                    placeholder.relative_to(ROOT).as_posix(),
                    [path.name for path in sorted(real_files)],
                )
            )

    assert invalid_placeholders == []
