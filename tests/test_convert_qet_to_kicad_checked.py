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


def test_qet_hight_pen_weight_is_native_two_unit_weight():
    adjustments: set[str] = set()
    stroke, _ = mod.style_expr(
        "line-style:normal;line-weight:hight;filling:none;color:black",
        adjustments,
    )

    assert "(width 0.508)" in stroke
    assert "line_weight_approximated:hight" not in adjustments


def test_qet_eleve_pen_weight_is_native_five_unit_weight():
    adjustments: set[str] = set()
    stroke, _ = mod.style_expr(
        "line-style:normal;line-weight:eleve;filling:none;color:black",
        adjustments,
    )

    assert "(width 1.27)" in stroke
    assert "line_weight_approximated:eleve" not in adjustments


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


def test_usertext_label_is_visible_static_text():
    drawing, adjustments = render(
        '<dynamic_text x="2" y="3" rotation="0" text_from="UserText" font="Liberation Sans,5">'
        '<text>n</text><info_name>label</info_name></dynamic_text>'
    )

    assert len(drawing) == 1
    assert '(text "n"' in drawing[0]
    assert "dynamic_text_staticized:UserText" in adjustments


def test_usertext_label_is_not_used_as_reference():
    root = ET.fromstring(
        '<definition><description>'
        '<dynamic_text text_from="ElementInfo"><text></text><info_name>label</info_name></dynamic_text>'
        '<dynamic_text text_from="UserText"><text>n</text><info_name>label</info_name></dynamic_text>'
        '</description></definition>'
    )

    assert mod.explicit_label(root, root.find("description")) == ""


def test_non_usertext_label_can_still_supply_reference():
    root = ET.fromstring(
        '<definition><description>'
        '<dynamic_text text_from="ElementInfo"><text>K1</text><info_name>label</info_name></dynamic_text>'
        '</description></definition>'
    )

    assert mod.explicit_label(root, root.find("description")) == "K1"


def test_triangle_line_endpoint_is_rendered_with_qet_geometry():
    drawing, adjustments = render(
        '<line x1="0" y1="0" x2="10" y2="0" end1="none" end2="triangle" '
        'length1="1.5" length2="1.5" '
        'style="line-style:normal;line-weight:normal;filling:black;color:black"/>'
    )

    assert len(drawing) == 2
    assert '(xy 0 0) (xy 2.159 0)' in drawing[0]
    assert '(xy 2.159 0)' in drawing[1]
    assert '(xy 2.159 -0.381)' in drawing[1]
    assert '(xy 2.54 0)' in drawing[1]
    assert '(xy 2.159 0.381)' in drawing[1]
    assert "line_endpoint_decoration_rendered:triangle" in adjustments
    assert "line_endpoint_decoration_omitted" not in adjustments


def test_triangle_line_endpoints_can_be_rendered_at_both_ends():
    drawing, adjustments = render(
        '<line x1="0" y1="0" x2="10" y2="0" end1="triangle" end2="triangle" '
        'length1="1.5" length2="1.5" '
        'style="line-style:normal;line-weight:normal;filling:black;color:black"/>'
    )

    assert len(drawing) == 3
    assert '(xy 0.381 0) (xy 2.159 0)' in drawing[0]
    assert sum('(xy 0 0)' in part or '(xy 2.54 0)' in part for part in drawing[1:]) == 2
    assert "line_endpoint_decoration_rendered:triangle" in adjustments
    assert "line_endpoint_decoration_omitted" not in adjustments


def test_simple_line_endpoint_preserves_qet_pen_offset():
    drawing, adjustments = render(
        '<line x1="0" y1="0" x2="10" y2="0" end1="none" end2="simple" '
        'length1="1.5" length2="1.5" '
        'style="line-style:normal;line-weight:normal;filling:none;color:black"/>'
    )

    assert len(drawing) == 2
    assert '(xy 0 0) (xy 2.413 0)' in drawing[0]
    assert '(xy 2.159 0.381)' in drawing[1]
    assert '(xy 2.54 0)' in drawing[1]
    assert '(xy 2.159 -0.381)' in drawing[1]
    assert "line_endpoint_decoration_rendered:simple" in adjustments
    assert "line_endpoint_decoration_omitted" not in adjustments


def test_diamond_line_endpoint_shortens_body_to_qet_a_point():
    drawing, adjustments = render(
        '<line x1="0" y1="0" x2="10" y2="0" end1="none" end2="diamond" '
        'length1="1.5" length2="1.5" '
        'style="line-style:normal;line-weight:normal;filling:none;color:black"/>'
    )

    assert len(drawing) == 2
    assert '(xy 0 0) (xy 1.778 0)' in drawing[0]
    assert '(xy 1.778 0)' in drawing[1]
    assert '(xy 2.159 -0.381)' in drawing[1]
    assert '(xy 2.54 0)' in drawing[1]
    assert '(xy 2.159 0.381)' in drawing[1]
    assert "line_endpoint_decoration_rendered:diamond" in adjustments
    assert "line_endpoint_decoration_omitted" not in adjustments


def test_circle_line_endpoint_preserves_qet_circle_and_pen_offset():
    drawing, adjustments = render(
        '<line x1="0" y1="0" x2="10" y2="0" end1="none" end2="circle" '
        'length1="1.5" length2="1.5" '
        'style="line-style:normal;line-weight:normal;filling:none;color:black"/>'
    )

    assert len(drawing) == 2
    assert '(xy 0 0) (xy 1.6891 0)' in drawing[0]
    assert '(circle (center 2.159 0) (radius 0.381)' in drawing[1]
    assert "line_endpoint_decoration_rendered:circle" in adjustments
    assert "line_endpoint_decoration_omitted" not in adjustments
