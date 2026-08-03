"""Extract safe, deterministic quality facts from KiCad footprint files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def extract_footprint_facts(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    name_match = re.search(r'^\(footprint\s+"([^"]+)"', text)
    version_match = re.search(r'\(version\s+(\d+)\)', text)
    generator_match = re.search(r'\(generator\s+([^\s\)]+)\)', text)
    library_name = path.parent.name.removesuffix(".pretty")
    footprint_name = name_match.group(1) if name_match else path.stem
    return {
        "element": f"{library_name}:{footprint_name}",
        "library_name": library_name,
        "footprint_name": footprint_name,
        "file_name": path.stem,
        "format_version": int(version_match.group(1)) if version_match else None,
        "generator": generator_match.group(1) if generator_match else None,
        "pad_count": len(re.findall(r'\(pad\s+', text)),
        "has_courtyard": bool(re.search(r'\bF\.CrtYd\b|\bB\.CrtYd\b', text)),
        "has_reference": bool(re.search(r'\(fp_text\s+reference\b', text)),
        "has_value": bool(re.search(r'\(fp_text\s+value\b', text)),
    }
