#!/usr/bin/env python3
"""Checked QET→KiCad entrypoint with QA and legacy-format corrections."""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence

import convert_qet_to_kicad as core
from qet_xml import SanitizationInfo, parse_qet_tree

_ORIGINAL_GRAPHICS = core.graphics
_ORIGINAL_EXPLICIT_LABEL = core.explicit_label
_ORIGINAL_CONVERT_ELEMENT = core.convert_element
_ORIGINAL_ET_PARSE = core.ET.parse
_RADIUS_ATTRIBUTES = ("rx", "ry", "radius")
_SANITIZED_PATHS: dict[Path, SanitizationInfo] = {}
_PLACEHOLDER_LABEL_RE = re.compile(r"^\?[^?]+\?$")
_NATIVE_FILLS = {"none", "black", "foreground", "color", "white", "background"}
_PATTERN_FILLS = {"bdiag", "fdiag", "hor", "ver", "diagcross", "cross"}


def _positive_numeric_attribute(node: ET.Element, names: Sequence[str]) -> bool:
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


def _clone(node: ET.Element) -> ET.Element:
    return ET.fromstring(ET.tostring(node, encoding="unicode"))


def _clone_without_zero_radii(node: ET.Element) -> ET.Element:
    clone = _clone(node)
    if not _positive_numeric_attribute(node, _RADIUS_ATTRIBUTES):
        for name in _RADIUS_ATTRIBUTES:
            clone.attrib.pop(name, None)
    return clone


def _replace_style_value(style: str, key: str, value: str) -> str:
    items = []
    replaced = False
    for item in style.split(";"):
        if ":" not in item:
            if item:
                items.append(item)
            continue
        k, v = item.split(":", 1)
        if k.strip().lower() == key:
            items.append(f"{k.strip()}:{value}")
            replaced = True
        else:
            items.append(f"{k.strip()}:{v.strip()}")
    if not replaced:
        items.append(f"{key}:{value}")
    return ";".join(items)


def _normalize_non_native_fill(node: ET.Element, adjustments: set[str]) -> ET.Element:
    style = node.get("style")
    if not style:
        return node
    filling = core.parse_style(style).get("filling", "none")
    if filling in _NATIVE_FILLS:
        return node

    clone = _clone(node)
    if filling in _PATTERN_FILLS:
        replacement = "black"
        adjustments.add(f"pattern_fill_mapped_to_outline:{filling}")
    elif filling.startswith("htmlwhite"):
        replacement = "white"
        adjustments.add(f"color_fill_mapped_to_background:{filling}")
    else:
        replacement = "black"
        adjustments.add(f"color_fill_mapped_to_outline:{filling}")
    clone.set("style", _replace_style_value(style, "filling", replacement))
    return clone


def _safe_et_parse(source, parser=None):
    if isinstance(source, (str, Path)):
        path = Path(source)
        tree, info = parse_qet_tree(path)
        if info.changed:
            _SANITIZED_PATHS[path.resolve()] = info
        return tree
    return _ORIGINAL_ET_PARSE(source, parser=parser)


def _usable_reference_label(value: str) -> str:
    value = value.strip()
    if not value or value == "_" or _PLACEHOLDER_LABEL_RE.fullmatch(value):
        return ""
    return value


def explicit_label(root: ET.Element, description: ET.Element | None) -> str:
    for cname in ("elementInformations", "element_informations"):
        container = root.find(cname)
        if container is not None:
            for node in list(container):
                if (node.get("name") or "").strip().lower() == "label":
                    value = _usable_reference_label(node.text or node.get("text") or "")
                    if value:
                        return value

    if description is not None:
        for node in description.iter():
            if (node.get("tagg") or node.get("tag") or "").strip().lower() == "label":
                value = _usable_reference_label(node.get("text") or node.text or "")
                if value:
                    return value
            if node.tag != "dynamic_text":
                continue
            if node.findtext("info_name", "").strip().lower() != "label":
                continue
            if (node.get("text_from") or "").strip().lower() == "usertext":
                continue
            value = _usable_reference_label(node.findtext("text", ""))
            if value:
                return value
    return ""


def _legacy_text_size(node: ET.Element) -> float:
    raw = node.get("size")
    if raw:
        try:
            return min(5.08, max(0.635, abs(float(raw)) * core.QET_UNIT_MM))
        except ValueError:
            pass
    return 1.27


def _render_dynamic_user_label(node: ET.Element, adjustments: set[str]) -> list[str] | None:
    if node.tag != "dynamic_text":
        return None
    info = node.findtext("info_name", "").strip().lower()
    text_from = (node.get("text_from") or "").strip().lower()
    text = node.findtext("text", "").strip()
    if info != "label" or text_from != "usertext" or not text or text == "_":
        return None

    x, y = core.xy(node.get("x"), node.get("y"))
    rotation = -float(node.get("rotation", 0) or 0)
    size = core.font_size(node.get("font"))
    adjustments.add("dynamic_text_staticized:UserText")
    return [
        f"      (text {core.quote(text)} (at {core.num(x)} {core.num(y)} {core.num(rotation)}) "
        f"(effects (font (size {core.num(size)} {core.num(size)}))))"
    ]


def _qet_triangle_points(
    end_point: tuple[float, float],
    other_point: tuple[float, float],
    length: float,
) -> tuple[tuple[float, float], list[tuple[float, float]]] | None:
    """Reproduce QET PartLine::fourEndPoints() for a Triangle line end."""
    dx = end_point[0] - other_point[0]
    dy = end_point[1] - other_point[1]
    line_length = math.hypot(dx, dy)
    if line_length <= 1e-12 or length <= 0:
        return None

    ux = dx / line_length * length
    uy = dy / line_length * length
    vx, vy = -uy, ux
    o = (end_point[0] - ux, end_point[1] - uy)
    b = (o[0] + vx, o[1] + vy)
    c = (o[0] - vx, o[1] - vy)
    return o, [o, b, end_point, c, o]


def _render_triangle_line_endings(node: ET.Element, adjustments: set[str]) -> list[str] | None:
    if node.tag != "line":
        return None

    end1 = (node.get("end1") or "none").strip().lower()
    end2 = (node.get("end2") or "none").strip().lower()
    if "triangle" not in {end1, end2}:
        return None
    if end1 not in {"none", "triangle"} or end2 not in {"none", "triangle"}:
        return None

    try:
        p1 = (float(node.get("x1", 0)), float(node.get("y1", 0)))
        p2 = (float(node.get("x2", 0)), float(node.get("y2", 0)))
        length1 = abs(float(node.get("length1", 1.5)))
        length2 = abs(float(node.get("length2", 1.5)))
    except ValueError:
        return None

    line_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    required = (length1 if end1 == "triangle" else 0.0) + (length2 if end2 == "triangle" else 0.0)
    if line_length + 1e-12 < required:
        return None

    start = p1
    stop = p2
    triangles: list[list[tuple[float, float]]] = []

    if end1 == "triangle":
        first = _qet_triangle_points(p1, p2, length1)
        if first is None:
            return None
        start, points = first
        triangles.append(points)

    if end2 == "triangle":
        second = _qet_triangle_points(p2, p1, length2)
        if second is None:
            return None
        stop, points = second
        triangles.append(points)

    style = node.get("style")
    result = [core.poly([core.xy(*start), core.xy(*stop)], style, adjustments)]
    result.extend(core.poly([core.xy(*point) for point in points], style, adjustments) for points in triangles)
    adjustments.add("line_endpoint_decoration_rendered:triangle")
    return result


def graphics(node: ET.Element, adjustments: set[str], unsupported) -> list[str]:
    if node.tag == "input":
        tagg = (node.get("tagg") or node.get("tag") or "none").strip().lower()
        if tagg == "label":
            adjustments.add("input_label_mapped_to_reference")
            return []

        text = (node.get("text") or "").strip()
        if not text:
            return []
        x, y = core.xy(node.get("x"), node.get("y"))
        size = _legacy_text_size(node)
        adjustments.add(f"input_staticized:{tagg or 'none'}")
        return [
            f"      (text {core.quote(text)} (at {core.num(x)} {core.num(y)} 0) "
            f"(effects (font (size {core.num(size)} {core.num(size)}))))"
        ]

    user_label = _render_dynamic_user_label(node, adjustments)
    if user_label is not None:
        return user_label

    triangle_line = _render_triangle_line_endings(node, adjustments)
    if triangle_line is not None:
        return triangle_line

    delegated = node
    if node.tag in {"rect", "rectangle"}:
        delegated = _clone_without_zero_radii(node)
    delegated = _normalize_non_native_fill(delegated, adjustments)

    result = _ORIGINAL_GRAPHICS(delegated, adjustments, unsupported)

    if node.tag == "dynamic_text":
        info = node.findtext("info_name", "").strip()
        text = node.findtext("text", "").strip()
        text_from = (node.get("text_from") or "").strip()
        if info.lower() != "label" and text and text != "_" and text_from:
            adjustments.add(f"dynamic_text_staticized:{text_from}")

    return result


def _add_adjustment_to_symbol(symbol_text: str, adjustment: str) -> tuple[str, bool]:
    pattern = re.compile(r'(\(property "QET_Adjustments" ")([^"]*)(")')
    match = pattern.search(symbol_text)
    if not match:
        return symbol_text, False
    current = match.group(2)
    parts = [] if not current or current == "none" else [p.strip() for p in current.split(";") if p.strip()]
    was_none = not parts
    if adjustment not in parts:
        parts.append(adjustment)
    replacement = match.group(1) + "; ".join(sorted(parts)) + match.group(3)
    return symbol_text[:match.start()] + replacement + symbol_text[match.end():], was_none


def convert_element(source_file: Path, source_root: Path, prefixes, stats, used) -> str:
    symbol = _ORIGINAL_CONVERT_ELEMENT(source_file, source_root, prefixes, stats, used)
    info = _SANITIZED_PATHS.get(source_file.resolve())
    if info is not None:
        counted_as_adjusted = False
        for marker in info.markers:
            symbol, was_none = _add_adjustment_to_symbol(symbol, marker)
            stats.adjustment_counts[marker] += 1
            counted_as_adjusted = counted_as_adjusted or was_none
        if counted_as_adjusted:
            stats.symbols_with_adjustments += 1
    return symbol


def install() -> None:
    core.ET.parse = _safe_et_parse
    core.explicit_label = explicit_label
    core.graphics = graphics
    core.convert_element = convert_element


def main(argv: Sequence[str] | None = None) -> int:
    install()
    return core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
