"""Reject legacy KiCad symbol-library IDs after the Z_ library migration."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
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
LEGACY_SYMBOL_ID_RE = re.compile(r"\bDIN_Electrical_Symbols:[A-Za-z0-9_]+\b")


def test_machine_readable_files_do_not_use_legacy_symbol_library_ids():
    stale_references = []
    for root in REFERENCE_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in REFERENCE_SUFFIXES:
                continue

            legacy_ids = sorted(set(LEGACY_SYMBOL_ID_RE.findall(path.read_text(encoding="utf-8"))))
            if legacy_ids:
                stale_references.append((path.relative_to(ROOT).as_posix(), legacy_ids))

    assert stale_references == []
