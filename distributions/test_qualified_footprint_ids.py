"""Validate qualified KiCad footprint IDs against per-footprint .pretty libraries."""
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


def test_qualified_footprint_ids_use_matching_library_and_existing_targets():
    invalid_ids = []

    for root in REFERENCE_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in REFERENCE_SUFFIXES:
                continue

            content = path.read_text(encoding="utf-8")
            for library_name, footprint_name in sorted(set(QUALIFIED_FOOTPRINT_ID_RE.findall(content))):
                reason = None
                if library_name != footprint_name:
                    reason = "library"
                elif not (FOOTPRINT_ROOT / f"{library_name}.pretty" / f"{footprint_name}.kicad_mod").is_file():
                    reason = "footprint"

                if reason:
                    invalid_ids.append(
                        (path.relative_to(ROOT).as_posix(), f"{library_name}:{footprint_name}", reason)
                    )

    assert invalid_ids == []
