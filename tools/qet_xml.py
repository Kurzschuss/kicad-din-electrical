#!/usr/bin/env python3
"""QElectroTech XML parsing helpers.

The official QET collection contains a few legacy XML defects. Recovery here is
intentionally narrow and deterministic: illegal XML 1.0 numeric character
references are replaced with U+FFFD, and a ``<name>`` that is demonstrably
missing its closing tag immediately before the next sibling ``<name>`` is
closed without inventing any missing text.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

_NUMERIC_REF_RE = re.compile(r"&#(?:(?P<dec>[0-9]+)|x(?P<hex>[0-9A-Fa-f]+));")
_NAMES_BLOCK_RE = re.compile(r"(<names\b[^>]*>)(.*?)(</names>)", re.DOTALL)
_UNCLOSED_NAME_BEFORE_SIBLING_RE = re.compile(
    r"(<name\b[^>]*>)(?P<body>(?:(?!</name>).)*?)(?P<ws>\s*)(?=<name\b)",
    re.DOTALL,
)
REPLACEMENT_CHAR = "\uFFFD"


@dataclass
class SanitizationInfo:
    invalid_codepoints: list[int] = field(default_factory=list)
    inserted_name_end_tags: int = 0

    @property
    def changed(self) -> bool:
        return bool(self.invalid_codepoints or self.inserted_name_end_tags)

    @property
    def markers(self) -> list[str]:
        markers: list[str] = []
        if self.invalid_codepoints:
            markers.append("invalid_xml_char_reference_sanitized")
        if self.inserted_name_end_tags:
            markers.append("missing_name_end_tag_sanitized")
        return markers


def xml10_codepoint_allowed(codepoint: int) -> bool:
    return (
        codepoint in (0x9, 0xA, 0xD)
        or 0x20 <= codepoint <= 0xD7FF
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def sanitize_invalid_numeric_references(text: str) -> tuple[str, list[int]]:
    replaced: list[int] = []

    def repl(match: re.Match[str]) -> str:
        raw = match.group("dec") or match.group("hex")
        base = 10 if match.group("dec") is not None else 16
        codepoint = int(raw, base)
        if xml10_codepoint_allowed(codepoint):
            return match.group(0)
        replaced.append(codepoint)
        return REPLACEMENT_CHAR

    return _NUMERIC_REF_RE.sub(repl, text), replaced


def sanitize_unclosed_name_siblings(text: str) -> tuple[str, int]:
    """Close an unclosed ``<name>`` only when the next sibling proves the defect.

    The repair is restricted to ``<names>...</names>`` containers. A match is
    possible only if another ``<name>`` starts before any ``</name>`` for the
    current entry, so valid name elements are left untouched.
    """
    inserted = 0

    def repair_block(block_match: re.Match[str]) -> str:
        nonlocal inserted
        opening, body, closing = block_match.groups()

        def repair_name(name_match: re.Match[str]) -> str:
            nonlocal inserted
            inserted += 1
            return (
                name_match.group(1)
                + name_match.group("body")
                + "</name>"
                + name_match.group("ws")
            )

        repaired = _UNCLOSED_NAME_BEFORE_SIBLING_RE.sub(repair_name, body)
        return opening + repaired + closing

    return _NAMES_BLOCK_RE.sub(repair_block, text), inserted


def sanitize_qet_xml(text: str) -> tuple[str, SanitizationInfo]:
    sanitized, invalid_codepoints = sanitize_invalid_numeric_references(text)
    sanitized, inserted_name_end_tags = sanitize_unclosed_name_siblings(sanitized)
    return sanitized, SanitizationInfo(
        invalid_codepoints=invalid_codepoints,
        inserted_name_end_tags=inserted_name_end_tags,
    )


def parse_qet_file(path: Path) -> tuple[ET.Element, SanitizationInfo]:
    text = path.read_text(encoding="utf-8")
    sanitized, info = sanitize_qet_xml(text)
    return ET.fromstring(sanitized), info


def parse_qet_tree(path: Path) -> tuple[ET.ElementTree, SanitizationInfo]:
    root, info = parse_qet_file(path)
    return ET.ElementTree(root), info
