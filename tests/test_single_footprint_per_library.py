"""Validate every footprint file inside populated .pretty libraries."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = ROOT / "footprints"
FOOTPRINT_NAME_RE = re.compile(r'^\(footprint "([^"]+)"', re.MULTILINE)


def test_all_footprints_in_pretty_directories_have_valid_matching_names():
    invalid_footprints = []

    for directory in sorted(
        path
        for path in FOOTPRINT_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(".pretty")
    ):
        for footprint_file in sorted(directory.glob("*.kicad_mod")):
            file_stem = footprint_file.stem
            content = footprint_file.read_text(encoding="utf-8")
            match = FOOTPRINT_NAME_RE.search(content)
            internal_name = match.group(1) if match else None

            reasons = []
            if not file_stem.startswith("Z_"):
                reasons.append("missing-Z-prefix")
            if internal_name != file_stem:
                reasons.append("internal-name-mismatch")

            if reasons:
                invalid_footprints.append(
                    (
                        footprint_file.relative_to(ROOT).as_posix(),
                        internal_name,
                        reasons,
                    )
                )

    assert invalid_footprints == []
