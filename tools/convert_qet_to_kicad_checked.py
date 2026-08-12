#!/usr/bin/env python3
"""Checked QET→KiCad entrypoint with QA corrections discovered in visual review.

The core converter stays intentionally small. This entrypoint hardens two QET
edge cases before the complete-library validation run:

1. QET often serializes square rectangles as ``rx=\"0\" ry=\"0\"``. Presence of
   those attributes alone must not be reported as a rounded-rectangle
   approximation.
2. Visible ``dynamic_text`` originating from QET ``UserText`` becomes static
   KiCad symbol text in the current converter. That loss of editability is a
   deliberate adaptation and therefore must be recorded.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence

# When this file is executed directly, its directory is on sys.path.
import convert_qet_to_kicad as core

_ORIGINAL_GRAPHICS = core.graphics
_RADIUS_ATTRIBUTES = ("rx", "ry", "radius")


def _positive_numeric_attribute(node: ET.Element, names: Sequence[str]) -> bool:
    """Return True only when at least one named numeric attribute is > 0.

    Malformed non-empty values are retained for the core converter, which then
    reports the shape as approximated rather than silently pretending it is a
    normal square rectangle.
    """
    for name in names:
        raw = node.get(name)
        if raw is None or raw.strip() == "":
            continue
        try:
            if abs(float(raw)) > 1e-9:
                return True
        except ValueError:
            return True
    return False


def _clone_without_zero_radii(node: ET.Element) -> ET.Element:
    clone = ET.fromstring(ET.tostring(node, encoding="unicode"))
    if not _positive_numeric_attribute(node, _RADIUS_ATTRIBUTES):
        for name in _RADIUS_ATTRIBUTES:
            clone.attrib.pop(name, None)
    return clone


def graphics(node: ET.Element, adjustments: set[str], unsupported) -> list[str]:
    """Apply QA corrections, then delegate geometry generation to the core."""
    delegated = node
    if node.tag in {"rect", "rectangle"}:
        delegated = _clone_without_zero_radii(node)

    result = _ORIGINAL_GRAPHICS(delegated, adjustments, unsupported)

    if node.tag == "dynamic_text":
        info = node.findtext("info_name", "").strip()
        text = node.findtext("text", "").strip()
        text_from = (node.get("text_from") or "").strip()
        if info.lower() != "label" and text and text != "_" and text_from:
            adjustments.add(f"dynamic_text_staticized:{text_from}")

    return result


def install() -> None:
    """Install the checked graphics policy into the core converter module."""
    core.graphics = graphics


def main(argv: Sequence[str] | None = None) -> int:
    install()
    return core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
