"""Validate qualified KiCad footprint IDs against the Z_DIN_Rail library."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
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
QUALIFIED_FOOTPRINT_ID_RE = re.compile(r"\b([A-Za-z0-9_]+):(Z_DIN_[A-Za-z0-9_]+)\b")
EXPECTED_LIBRARY = "Z_DIN_Rail"


def test_qualified_footprint_ids_use_expected_library_and_existing_targets():
    available_footprints = {path.stem for path in FOOTPRINT_ROOT.rglob("*.kicad_mod")}
    invalid_ids = []

    for root in REFERENCE_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in REFERENCE_SUFFIXES:
                continue

            content = path.read_text(encoding="utf-8")
            for library_name, footprint_name in sorted(set(QUALIFIED_FOOTPRINT_ID_RE.findall(content))):
                reason = None
                if library_name != EXPECTED_LIBRARY:
                    reason = "library"
                elif footprint_name not in available_footprints:
                    reason = "footprint"

                if reason:
                    invalid_ids.append(
                        (path.relative_to(ROOT).as_posix(), f"{library_name}:{footprint_name}", reason)
                    )

    assert invalid_ids == []
