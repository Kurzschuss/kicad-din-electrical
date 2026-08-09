#!/usr/bin/env python3
"""Erzeugt reproduzierbare SVG-Vorschauen aus KiCad-Symbolbibliotheken.

Unterstützt Rechtecke, Polylinien und Pins. Bei Bibliotheken mit mehreren
Top-Level-Symbolen wird jede Vorschau ausschließlich aus dem zugehörigen
Symbolblock erzeugt. Die Vorschaugeometrie wird automatisch mit Sicherheitsrand
in die feste SVG-Fläche eingepasst. Die Quelldateien werden nicht verändert.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from math import cos, radians, sin
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
POLYLINE_START_RE = re.compile(r'\(polyline\b')
POINT_RE = re.compile(r'\(xy\s+(-?[\d.]+)\s+(-?[\d.]+)\)')

PREVIEW_CENTER_X = 120.0
PREVIEW_CENTER_Y = 78.0
PREVIEW_MAX_SCALE = 12.0
PREVIEW_USABLE_WIDTH = 198.0
PREVIEW_USABLE_HEIGHT = 122.0


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


@dataclass(frozen=True)
class Polyline:
    points: tuple[tuple[float, float], ...]
    filled: bool = False


def _balanced_expression(text: str, start: int) -> str:
    """Liefert den geklammerten S-Expression-Block ab ``start``."""
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError("Unvollständiger KiCad-S-Expression-Block")


def symbol_blocks(text: str) -> dict[str, str]:
    """Trennt Top-Level-Symbole, damit Geometrie nicht bibliotheksweit vermischt wird."""
    return {
        match.group(1): _balanced_expression(text, match.start())
        for match in TOP_LEVEL_SYMBOL_RE.finditer(text)
    }


def symbol_names(text: str) -> list[str]:
    return list(symbol_blocks(text))


def parse_rectangles(text: str) -> list[Rectangle]:
    return [Rectangle(*(float(value) for value in match)) for match in RECTANGLE_RE.findall(text)]


def parse_pins(text: str) -> list[Pin]:
    return [Pin(*(float(value) for value in match)) for match in PIN_RE.findall(text)]


def parse_polylines(text: str) -> list[Polyline]:
    result: list[Polyline] = []
    for match in POLYLINE_START_RE.finditer(text):
        block = _balanced_expression(text, match.start())
        points = tuple((float(x), float(y)) for x, y in POINT_RE.findall(block))
        if len(points) < 2:
            continue
        result.append(Polyline(points=points, filled="(fill (type outline))" in block))
    return result


def _pin_endpoint(pin: Pin) -> tuple[float, float]:
    angle = radians(pin.angle)
    return (
        pin.x + pin.length * cos(angle),
        pin.y + pin.length * sin(angle),
    )


def _logical_points(
    rectangles: list[Rectangle],
    pins: list[Pin],
    polylines: list[Polyline],
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in rectangles:
        points.extend(((item.x1, item.y1), (item.x2, item.y2)))
    for item in polylines:
        points.extend(item.points)
    for item in pins:
        points.extend(((item.x, item.y), _pin_endpoint(item)))
    return points


def _preview_projector(
    rectangles: list[Rectangle],
    pins: list[Pin],
    polylines: list[Polyline],
):
    """Erzeugt eine Projektion, die die komplette Symbolgeometrie sicher einpasst."""
    points = _logical_points(rectangles, pins, polylines)
    if not points:
        return lambda x, y: (PREVIEW_CENTER_X + x, PREVIEW_CENTER_Y - y)

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    minimum_x, maximum_x = min(xs), max(xs)
    minimum_y, maximum_y = min(ys), max(ys)
    width = max(maximum_x - minimum_x, 1.0)
    height = max(maximum_y - minimum_y, 1.0)
    scale = min(
        PREVIEW_MAX_SCALE,
        PREVIEW_USABLE_WIDTH / width,
        PREVIEW_USABLE_HEIGHT / height,
    )
    center_x = (minimum_x + maximum_x) / 2.0
    center_y = (minimum_y + maximum_y) / 2.0

    def project(x: float, y: float) -> tuple[float, float]:
        return (
            PREVIEW_CENTER_X + (x - center_x) * scale,
            PREVIEW_CENTER_Y - (y - center_y) * scale,
        )

    return project


def render_svg(
    library: str,
    symbol: str,
    rectangles: list[Rectangle],
    pins: list[Pin],
    polylines: list[Polyline] | None = None,
) -> str:
    source_polylines = polylines or []
    project = _preview_projector(rectangles, pins, source_polylines)
    shapes: list[str] = []
    for item in rectangles:
        x1, y1 = project(item.x1, item.y1)
        x2, y2 = project(item.x2, item.y2)
        shapes.append(
            f'<rect x="{min(x1, x2):.2f}" y="{min(y1, y2):.2f}" '
            f'width="{abs(x2-x1):.2f}" height="{abs(y2-y1):.2f}" '
            'fill="none" stroke="currentColor" stroke-width="2"/>'
        )
    for item in source_polylines:
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in (project(x, y) for x, y in item.points))
        tag = "polygon" if item.filled else "polyline"
        fill = "currentColor" if item.filled else "none"
        shapes.append(
            f'<{tag} points="{points}" fill="{fill}" stroke="currentColor" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
        )
    for item in pins:
        x1, y1 = project(item.x, item.y)
        endpoint_x, endpoint_y = _pin_endpoint(item)
        x2, y2 = project(endpoint_x, endpoint_y)
        shapes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            'stroke="currentColor" stroke-width="2"/>'
        )

    if not shapes:
        shapes.append('<text x="120" y="78" text-anchor="middle" font-size="13">Keine unterstützte Grafik</text>')

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
        for name, block in symbol_blocks(text).items():
            target = OUTPUT_ROOT / source.stem / f"{name}.svg"
            files[target] = render_svg(
                source.stem,
                name,
                parse_rectangles(block),
                parse_pins(block),
                parse_polylines(block),
            )
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
