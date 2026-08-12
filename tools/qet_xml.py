#!/usr/bin/env python3
"""QElectroTech XML parsing helpers.

Some legacy QET element files contain numeric character references that are not
legal in XML 1.0 (for example ``&#11;``). The official QET collection still
contains such files, so conversion must recover deterministically without
silently inventing the missing character.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

_NUMERIC_REF_RE = re.compile(r"&#(?:(?P<dec>[0-9]+)|x(?P<hex>[0-9A-Fa-f]+));")
REPLACEMENT_CHAR = "\uFFFD"


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


def parse_qet_file(path: Path) -> tuple[ET.Element, list[int]]:
    text = path.read_text(encoding="utf-8")
    sanitized, replaced = sanitize_invalid_numeric_references(text)
    return ET.fromstring(sanitized), replaced


def parse_qet_tree(path: Path) -> tuple[ET.ElementTree, list[int]]:
    root, replaced = parse_qet_file(path)
    return ET.ElementTree(root), replaced
