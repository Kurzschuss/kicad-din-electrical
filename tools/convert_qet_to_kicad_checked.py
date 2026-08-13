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
_ORIGINAL_STYLE_EXPR = core.style_expr
_ORIGINAL_ET_PARSE = core.ET.parse
_RADIUS_ATTRIBUTES = ("rx", "ry", "radius")
_SANITIZED_PATHS: dict[Path, SanitizationInfo] = {}
_PLACEHOLDER_LABEL_RE = re.compile(r"^\?[^?]+\?$")
_NATIVE_FILLS = {"none", "black", "foreground", "color", "white", "background"}
_PATTERN_FILLS = {"bdiag", "fdiag", "hor", "ver", "diagcross", "cross"}
_QET_END_REQUIRED_LENGTHS = {
    "none": 0,
    "circle": 2,
    "diamond": 2,
    "simple": 1,
    "triangle": 1,
}
_QET_PEN_WEIGHTS = {
    "none": 0.0,
    "thin": 0.0,
    "normal": 1.0,
    "hight": 2.0,
    "high": 2.0,
    "ultra": 2.0,
    "eleve": 5.0,
    "big": 5.0,
}


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


def _normalize_legacy_qet_typos(node: ET.Element, adjustments: set[str]) -> ET.Element:
    """Repair known legacy QET spelling errors while recording every correction."""
    clone: ET.Element | None = None

    for attr in ("end1", "end2"):
        if (node.get(attr) or "").strip().lower() == "ncne":
            if clone is None:
                clone = _clone(node)
            clone.set(attr, "none")
            adjustments.add("legacy_qet_typo_normalized:end=ncne->none")

    current = clone if clone is not None else node
    style = current.get("style")
    if not style:
        return current

    parsed = core.parse_style(style)
    replacements = []
    if parsed.get("line-style") == "ncrmal":
        replacements.append(("line-style", "normal", "legacy_qet_typo_normalized:line-style=ncrmal->normal"))
    if parsed.get("line-weight") == "ncrmal":
        replacements.append(("line-weight", "normal", "legacy_qet_typo_normalized:line-weight=ncrmal->normal"))
    if parsed.get("filling") == "ncne":
        replacements.append(("filling", "none", "legacy_qet_typo_normalized:filling=ncne->none"))

    if not replacements:
        return current
    if clone is None:
        clone = _clone(node)
        style = clone.get("style") or ""
    else:
        style = clone.get("style") or ""
    for key, value, marker in replacements:
        style = _replace_style_value(style, key, value)
        adjustments.add(marker)
    clone.set("style", style)
    return clone


def style_expr(style: str | None, adjustments: set[str]) -> tuple[str, str]:
    """Honor canonical QET hight/eleve pen weights before delegating style mapping."""
    parsed = core.parse_style(style)
    weight = parsed.get("line-weight", "normal")
    if weight not in {"hight", "eleve"}:
        return _ORIGINAL_STYLE_EXPR(style, adjustments)

    normalized = _replace_style_value(style or "", "line-weight", "normal")
    stroke, fill = _ORIGINAL_STYLE_EXPR(normalized, adjustments)
    width_mm = _QET_PEN_WEIGHTS[weight] * core.QET_UNIT_MM
    stroke = re.sub(
        r"\(stroke \(width [^)]+\)",
        f"(stroke (width {core.num(width_mm)})",
        stroke,
        count=1,
    )
    return stroke, fill


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


def _qet_four_end_points(
    end_point: tuple[float, float],
    other_point: tuple[float, float],
    length: float,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]] | None:
    """Reproduce QET PartLine::fourEndPoints(): O, A, B, C."""
    dx = end_point[0] - other_point[0]
    dy = end_point[1] - other_point[1]
    line_length = math.hypot(dx, dy)
    if line_length <= 1e-12 or length <= 0:
        return None

    ux = dx / line_length * length
    uy = dy / line_length * length
    vx, vy = -uy, ux
    o = (end_point[0] - ux, end_point[1] - uy)
    a = (o[0] - ux, o[1] - uy)
    b = (o[0] + vx, o[1] + vy)
    c = (o[0] - vx, o[1] - vy)
    return o, a, b, c


def _point_at(
    start: tuple[float, float],
    stop: tuple[float, float],
    fraction: float,
) -> tuple[float, float]:
    return (
        start[0] + (stop[0] - start[0]) * fraction,
        start[1] + (stop[1] - start[1]) * fraction,
    )


def _qet_pen_weight(style: str | None) -> float:
    weight = core.parse_style(style).get("line-weight", "normal")
    return _QET_PEN_WEIGHTS.get(weight, 1.0)


def _render_qet_end_shape(
    end_type: str,
    end_point: tuple[float, float],
    other_point: tuple[float, float],
    length: float,
    style: str | None,
    adjustments: set[str],
) -> tuple[tuple[float, float], list[str]] | None:
    points = _qet_four_end_points(end_point, other_point, length)
    if points is None:
        return None
    o, a, b, c = points

    if end_type == "circle":
        stroke, fill = core.style_expr(style, adjustments)
        cx, cy = core.xy(*o)
        primitive = (
            f"      (circle (center {core.num(cx)} {core.num(cy)}) "
            f"(radius {core.num(core.mm(length))}) {stroke} {fill})"
        )
        return a, [primitive]
    if end_type == "diamond":
        polygon = [a, b, end_point, c, a]
        return a, [core.poly([core.xy(*point) for point in polygon], style, adjustments)]
    if end_type == "simple":
        polygon = [c, end_point, b, c]
        return end_point, [core.poly([core.xy(*point) for point in polygon], style, adjustments)]
    if end_type == "triangle":
        polygon = [o, b, end_point, c, o]
        return o, [core.poly([core.xy(*point) for point in polygon], style, adjustments)]
    return None


def _render_qet_line_endings(node: ET.Element, adjustments: set[str]) -> list[str] | None:
    if node.tag != "line":
        return None

    end1 = (node.get("end1") or "none").strip().lower()
    end2 = (node.get("end2") or "none").strip().lower()
    if end1 == end2 == "none":
        return None
    if end1 not in _QET_END_REQUIRED_LENGTHS or end2 not in _QET_END_REQUIRED_LENGTHS:
        return None

    try:
        p1 = (float(node.get("x1", 0)), float(node.get("y1", 0)))
        p2 = (float(node.get("x2", 0)), float(node.get("y2", 0)))
        length1 = abs(float(node.get("length1", 1.5)))
        length2 = abs(float(node.get("length2", 1.5)))
    except ValueError:
        return None

    line_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    if line_length <= 1e-12:
        return None

    style = node.get("style")
    reduced = line_length - length1 * _QET_END_REQUIRED_LENGTHS[end1]
    draw_first = end1 != "none" and reduced >= -1e-12
    if draw_first:
        reduced -= length2 * _QET_END_REQUIRED_LENGTHS[end2]
    else:
        reduced = line_length - length2 * _QET_END_REQUIRED_LENGTHS[end2]
    draw_second = end2 != "none" and reduced >= -1e-12

    start = p1
    stop = p2
    primitives: list[str] = []
    pen_weight = _qet_pen_weight(style)

    if draw_first:
        first = _render_qet_end_shape(end1, p1, p2, length1, style, adjustments)
        if first is None:
            return None
        start, rendered = first
        primitives.extend(rendered)
        adjustments.add(f"line_endpoint_decoration_rendered:{end1}")
        if pen_weight and end1 in {"simple", "circle"}:
            start = _point_at(start, p2, (pen_weight / 2.0) / line_length)
    elif end1 != "none":
        adjustments.add(f"line_endpoint_qet_suppressed_short:{end1}")

    if draw_second:
        second = _render_qet_end_shape(end2, p2, p1, length2, style, adjustments)
        if second is None:
            return None
        stop, rendered = second
        primitives.extend(rendered)
        adjustments.add(f"line_endpoint_decoration_rendered:{end2}")
        if pen_weight and end2 in {"simple", "circle"}:
            stop = _point_at(p1, stop, (line_length - (pen_weight / 2.0)) / line_length)
    elif end2 != "none":
        adjustments.add(f"line_endpoint_qet_suppressed_short:{end2}")

    body = core.poly([core.xy(*start), core.xy(*stop)], style, adjustments)
    return [body, *primitives]


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

    delegated = _normalize_legacy_qet_typos(node, adjustments)
    if delegated.tag in {"rect", "rectangle"}:
        delegated = _clone_without_zero_radii(delegated)
    delegated = _normalize_non_native_fill(delegated, adjustments)

    line_with_endings = _render_qet_line_endings(delegated, adjustments)
    if line_with_endings is not None:
        return line_with_endings

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
    core.style_expr = style_expr
    core.graphics = graphics
    core.convert_element = convert_element


def main(argv: Sequence[str] | None = None) -> int:
    install()
    return core.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
