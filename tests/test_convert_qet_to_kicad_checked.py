from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

MODULE_PATH = TOOLS / "convert_qet_to_kicad_checked.py"
SPEC = importlib.util.spec_from_file_location("convert_qet_to_kicad_checked", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def render(xml: str) -> tuple[list[str], set[str]]:
    node = ET.fromstring(xml)
    adjustments: set[str] = set()
    result = mod.graphics(node, adjustments, Counter())
    return result, adjustments


def test_zero_rx_ry_is_not_reported_as_rounded_rectangle():
    _, adjustments = render(
        '<rect x="0" y="0" width="10" height="5" rx="0" ry="0" '
        'style="line-style:normal;line-weight:normal;filling:none;color:black"/>'
    )
    assert "rounded_rectangle_approximated" not in adjustments


def test_positive_radius_still_reports_rounded_rectangle_approximation():
    _, adjustments = render(
        '<rect x="0" y="0" width="10" height="5" rx="2" ry="2" '
        'style="line-style:normal;line-weight:normal;filling:none;color:black"/>'
    )
    assert "rounded_rectangle_approximated" in adjustments


def test_visible_user_text_is_marked_as_staticized():
    drawing, adjustments = render(
        '<dynamic_text x="0" y="0" text_from="UserText" font="Liberation Sans,9">'
        '<text>Kabel</text></dynamic_text>'
    )
    assert drawing
    assert "dynamic_text_staticized:UserText" in adjustments


def test_label_dynamic_text_is_not_staticized():
    _, adjustments = render(
        '<dynamic_text x="0" y="0" text_from="ElementInfo" font="Liberation Sans,9">'
        '<text>M1</text><info_name>label</info_name></dynamic_text>'
    )
    assert "dynamic_text_staticized:ElementInfo" not in adjustments
