from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location(
    "convert_qet_to_kicad_checked_fill", TOOLS / "convert_qet_to_kicad_checked.py"
)
assert SPEC and SPEC.loader
checked = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checked
SPEC.loader.exec_module(checked)


def render(xml: str):
    adjustments: set[str] = set()
    drawing = checked.graphics(ET.fromstring(xml), adjustments, {})
    return drawing, adjustments


def test_colored_fill_becomes_monochrome_solid_fill():
    drawing, adjustments = render(
        '<rect x="0" y="0" width="10" height="10" rx="0" ry="0" '
        'style="line-style:normal;line-weight:normal;filling:blue;color:black"/>'
    )
    assert "(fill (type outline))" in drawing[0]
    assert "color_fill_mapped_to_outline:blue" in adjustments
    assert "fill_style_approximated:blue" not in adjustments


def test_white_named_fill_becomes_background_fill():
    drawing, adjustments = render(
        '<rect x="0" y="0" width="10" height="10" '
        'style="line-style:normal;line-weight:normal;filling:htmlwhitesnow;color:black"/>'
    )
    assert "(fill (type background))" in drawing[0]
    assert "color_fill_mapped_to_background:htmlwhitesnow" in adjustments


def test_hatch_fill_is_preserved_as_solid_monochrome_with_marker():
    drawing, adjustments = render(
        '<polygon x1="0" y1="0" x2="10" y2="0" x3="10" y3="10" '
        'style="line-style:normal;line-weight:normal;filling:fdiag;color:black"/>'
    )
    assert "(fill (type outline))" in drawing[0]
    assert "pattern_fill_mapped_to_outline:fdiag" in adjustments
