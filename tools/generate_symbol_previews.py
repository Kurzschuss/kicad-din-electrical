#!/usr/bin/env python3
"""Erzeugt einfache SVG-Vorschauen aus KiCad-Symbolbibliotheken.

Phase 1 unterstützt die in den vorhandenen Bibliotheken verwendeten
Grundelemente Rechteck und Pin. Die Quelldateien werden nicht verändert.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL_ROOT = REPO_ROOT / "symbols"
OUTPUT_ROOT = REPO_ROOT / "docs" / "site" / "symbol-previews"

TOP_LEVEL_SYMBOL_RE = re.compile(r'^  \(symbol "([^"]+)"', re.MULTILINE)
RECTANGLE_RE = re.compile(
    r'\(rectangle\s+\(start\s+(-?[\d.]+)\s+(-?[\d.]+)\)\s+'
    r'\(end\s+(-?[\d.]+)\s+(-?[\d.]+)\)'
)
PIN_RE = re.compile(
    r'\(pin\s+\S+\s+\S+\s+\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\)\s+'
    r'\(length\s+(-?[\d.]+)\)'
)


@dataclass(frozen=True)
class Rectangle:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Pin:
    x: float
    y: float
    angle: float
    length: float


def symbol_names(text: str) -> list[str]:
    return TOP_LEVEL_SYMBOL_RE.findall(text)


def parse_rectangles(text: str) -> list[Rectangle]:
    return [Rectangle(*(float(value) for value in match)) for match in RECTANGLE_RE.findall(text)]


def parse_pins(text: str) -> list[Pin]:
    return [Pin(*(float(value) for value in match)) for match in PIN_RE.findall(text)]


def _point(x: float, y: float, scale: float = 12.0) -> tuple[float, float]:
    return 120 + x * scale, 90 - y * scale


def render_svg(library: str, symbol: str, rectangles: list[Rectangle], pins: list[Pin]) -> str:
    shapes: list[str] = []
    for item in rectangles:
        x1, y1 = _point(item.x1, item.y1)
        x2, y2 = _point(item.x2, item.y2)
        shapes.append(
            f'<rect x="{min(x1, x2):.2f}" y="{min(y1, y2):.2f}" '
            f'width="{abs(x2-x1):.2f}" height="{abs(y2-y1):.2f}" '
            'fill="none" stroke="currentColor" stroke-width="2"/>'
        )
    for item in pins:
        x1, y1 = _point(item.x, item.y)
        radians = item.angle * 3.141592653589793 / 180.0
        x2 = x1 + item.length * 12.0 * __import__("math").cos(radians)
        y2 = y1 - item.length * 12.0 * __import__("math").sin(radians)
        shapes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            'stroke="currentColor" stroke-width="2"/>'
        )

    if not shapes:
        shapes.append('<text x="120" y="90" text-anchor="middle" font-size="13">Keine unterstützte Grafik</text>')

    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 180" role="img">',
        f'  <title>{escape(library)}: {escape(symbol)}</title>',
        '  <rect x="1" y="1" width="238" height="178" rx="8" fill="none" stroke="currentColor" opacity="0.25"/>',
        *[f"  {shape}" for shape in shapes],
        f'  <text x="120" y="164" text-anchor="middle" font-size="12">{escape(symbol)}</text>',
        '</svg>',
        '',
    ])


def generated_files(symbol_root: Path = SYMBOL_ROOT) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for source in sorted(symbol_root.glob("Z_*.kicad_sym"), key=lambda path: path.name.casefold()):
        text = source.read_text(encoding="utf-8")
        names = symbol_names(text)
        if not names:
            continue
        rectangles = parse_rectangles(text)
        pins = parse_pins(text)
        for name in names:
            target = OUTPUT_ROOT / source.stem / f"{name}.svg"
            files[target] = render_svg(source.stem, name, rectangles, pins)
    return files


def write_previews(files: dict[Path, str]) -> None:
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_previews(files: dict[Path, str]) -> bool:
    expected_paths = set(files)
    actual_paths = set(OUTPUT_ROOT.glob("Z_*/*.svg")) if OUTPUT_ROOT.is_dir() else set()
    if expected_paths != actual_paths:
        return False
    return all(path.read_text(encoding="utf-8") == content for path, content in files.items())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob alle Vorschauen aktuell sind")
    args = parser.parse_args()
    files = generated_files()
    if args.check:
        if check_previews(files):
            print(f"{len(files)} Symbolvorschauen sind aktuell.")
            return 0
        print("Die Symbolvorschauen fehlen oder sind nicht aktuell.", file=sys.stderr)
        return 1
    write_previews(files)
    print(f"{len(files)} Symbolvorschauen erzeugt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
