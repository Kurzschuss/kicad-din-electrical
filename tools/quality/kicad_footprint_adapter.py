"""Extract safe, deterministic quality facts from KiCad footprint files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _courtyard_rect(text: str) -> tuple[float | None, float | None, float | None]:
    for segment in text.split("(fp_rect")[1:]:
        if re.search(r'\(layer\s+"(?:F|B)\.CrtYd"\)', segment) is None:
            continue
        start_match = re.search(r'\(start\s+(-?[\d.]+)\s+(-?[\d.]+)\)', segment)
        end_match = re.search(r'\(end\s+(-?[\d.]+)\s+(-?[\d.]+)\)', segment)
        width_match = re.search(r'\(stroke\s+\(width\s+([\d.]+)\)', segment)
        if not (start_match and end_match and width_match):
            continue
        x1, y1 = (float(value) for value in start_match.groups())
        x2, y2 = (float(value) for value in end_match.groups())
        line_width = float(width_match.group(1))
        return abs(x2 - x1), abs(y2 - y1), line_width
    return None, None, None


def extract_footprint_facts(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    name_match = re.search(r'^\(footprint\s+"([^"]+)"', text)
    version_match = re.search(r'\(version\s+(\d+)\)', text)
    generator_match = re.search(r'\(generator\s+([^\s\)]+)\)', text)
    library_name = path.parent.name.removesuffix(".pretty")
    footprint_name = name_match.group(1) if name_match else path.stem
    courtyard_width, courtyard_height, courtyard_line_width = _courtyard_rect(text)
    return {
        "element": f"{library_name}:{footprint_name}",
        "library_name": library_name,
        "footprint_name": footprint_name,
        "file_name": path.stem,
        "format_version": int(version_match.group(1)) if version_match else None,
        "generator": generator_match.group(1) if generator_match else None,
        "pad_count": len(re.findall(r'\(pad\s+', text)),
        "has_courtyard": courtyard_width is not None,
        "courtyard_closed": courtyard_width is not None and courtyard_height is not None,
        "courtyard_width_mm": courtyard_width,
        "courtyard_height_mm": courtyard_height,
        "courtyard_line_width_mm": courtyard_line_width,
        "has_reference": bool(re.search(r'\(fp_text\s+reference\b', text)),
        "has_value": bool(re.search(r'\(fp_text\s+value\b', text)),
        "has_fab_outline": bool(re.search(r'\(layer\s+"(?:F|B)\.Fab"\)', text)),
    }
