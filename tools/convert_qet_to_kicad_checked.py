#!/usr/bin/env python3
"""Checked QET→KiCad entrypoint with QA and legacy-format corrections."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence

import convert_qet_to_kicad as core
from qet_xml import parse_qet_tree

_ORIGINAL_GRAPHICS = core.graphics
_ORIGINAL_EXPLICIT_LABEL = core.explicit_label
_ORIGINAL_CONVERT_ELEMENT = core.convert_element
_ORIGINAL_ET_PARSE = core.ET.parse
_RADIUS_ATTRIBUTES = ("rx", "ry", "radius")
_SANITIZED_PATHS: dict[Path, list[int]] = {}
_PLACEHOLDER_LABEL_RE = re.compile(r"^\?[^?]+\?$")


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


def _clone_without_zero_radii(node: ET.Element) -> ET.Element:
    clone = ET.fromstring(ET.tostring(node, encoding="unicode"))
    if not _positive_numeric_attribute(node, _RADIUS_ATTRIBUTES):
        for name in _RADIUS_ATTRIBUTES:
            clone.attrib.pop(name, None)
    return clone


def _safe_et_parse(source, parser=None):
    if isinstance(source, (str, Path)):
        path = Path(source)
        tree, replaced = parse_qet_tree(path)
        if replaced:
            _SANITIZED_PATHS[path.resolve()] = replaced
        return tree
    return _ORIGINAL_ET_PARSE(source, parser=parser)


def explicit_label(root: ET.Element, description: ET.Element | None) -> str:
    value = _ORIGINAL_EXPLICIT_LABEL(root, description)
    # Legacy QET <input tagg="label" text="?U?"> stores a UI placeholder,
    # not a reference-prefix decision. Let qet_labels.xml/fallback policy decide.
    if value and _PLACEHOLDER_LABEL_RE.fullmatch(value):
        return ""
    return value


def _legacy_text_size(node: ET.Element) -> float:
    raw = node.get("size")
    if raw:
        try:
            return min(5.08, max(0.635, abs(float(raw)) * core.QET_UNIT_MM))
        except ValueError:
            pass
    return 1.27


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
    path = source_file.resolve()
    if path in _SANITIZED_PATHS:
        marker = "invalid_xml_char_reference_sanitized"
        symbol, was_none = _add_adjustment_to_symbol(symbol, marker)
        stats.adjustment_counts[marker] += 1
        if was_none:
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
