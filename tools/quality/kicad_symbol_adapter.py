"""Extract deterministic quality facts from a KiCad symbol library.

This adapter intentionally supports a small, audited subset of the KiCad
S-expression format. It does not execute file content and it does not try to
replace KiCad's own parser. Its purpose is to expose stable facts to the
project's data-driven Z_ rule engine.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

MM_PER_MIL = 0.0254


def _to_mil(value_mm: str) -> int:
    return round(float(value_mm) / MM_PER_MIL)


def extract_symbol_facts(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    library_name = path.stem

    pin_positions = [
        (_to_mil(x), _to_mil(y))
        for x, y in re.findall(r"\(pin\s+[^\n]*?\(at\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+", text)
    ]
    pin_lengths = [
        _to_mil(value)
        for value in re.findall(r"\(pin\s+[^\n]*?\(length\s+(-?\d+(?:\.\d+)?)\)", text)
    ]
    line_widths = [
        _to_mil(value)
        for value in re.findall(r"\(stroke\s+\(width\s+(-?\d+(?:\.\d+)?)\)", text)
    ]

    primary_text_sizes = []
    for property_name in ("Reference", "Value"):
        match = re.search(
            rf'\(property\s+"{property_name}".*?\(font\s+\(size\s+(-?\d+(?:\.\d+)?)\s+',
            text,
            re.DOTALL,
        )
        if match:
            primary_text_sizes.append(_to_mil(match.group(1)))

    connection_grid_mil = 100 if pin_positions and all(
        x % 100 == 0 and y % 100 == 0 for x, y in pin_positions
    ) else None

    footprint_match = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', text)
    footprint_value = footprint_match.group(1) if footprint_match else None

    return {
        "element": f"{path.as_posix()} – {library_name}",
        "library_name": library_name,
        "connection_grid_mil": connection_grid_mil,
        "pin_length_mil": pin_lengths[0] if pin_lengths and len(set(pin_lengths)) == 1 else None,
        "line_width_mil": line_widths[0] if line_widths and len(set(line_widths)) == 1 else None,
        "text_size_mil": primary_text_sizes[0]
        if primary_text_sizes and len(set(primary_text_sizes)) == 1
        else None,
        "footprint_policy_valid": footprint_value not in (None, ""),
        "footprint_value": footprint_value,
    }
