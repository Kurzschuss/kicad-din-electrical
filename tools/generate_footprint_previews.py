#!/usr/bin/env python3
"""Erzeugt deterministische SVG-Vorschauen aus KiCad-Footprints.

Die erste Ausbaustufe unterstützt rechteckige Geometrien auf F.Fab und
F.CrtYd. Die Quelldateien werden nicht verändert und KiCad wird nicht benötigt.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = REPO_ROOT / "footprints"
OUTPUT_ROOT = REPO_ROOT / "docs" / "site" / "footprint-previews"

NAME_RE = re.compile(r'^\(footprint\s+"([^"]+)"')
RECT_RE = re.compile(
    r'\(fp_rect\s+\(start\s+(-?[\d.]+)\s+(-?[\d.]+)\)\s+'
    r'\(end\s+(-?[\d.]+)\s+(-?[\d.]+)\).*?'
    r'\(layer\s+"((?:F\.Fab)|(?:F\.CrtYd))"\)',
    re.DOTALL,
)


@dataclass(frozen=True)
class FootprintRectangle:
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str


def footprint_name(text: str, fallback: str) -> str:
    match = NAME_RE.search(text)
    return match.group(1) if match else fallback


def parse_rectangles(text: str) -> list[FootprintRectangle]:
    return [
        FootprintRectangle(float(x1), float(y1), float(x2), float(y2), layer)
        for x1, y1, x2, y2, layer in RECT_RE.findall(text)
    ]


def _bounds(rectangles: list[FootprintRectangle]) -> tuple[float, float, float, float]:
    xs = [value for item in rectangles for value in (item.x1, item.x2)]
    ys = [value for item in rectangles for value in (item.y1, item.y2)]
    return min(xs), min(ys), max(xs), max(ys)


def render_svg(name: str, rectangles: list[FootprintRectangle]) -> str:
    width, height, margin = 260.0, 210.0, 24.0
    shapes: list[str] = []
    if rectangles:
        min_x, min_y, max_x, max_y = _bounds(rectangles)
        source_width = max(max_x - min_x, 1.0)
        source_height = max(max_y - min_y, 1.0)
        scale = min((width - 2 * margin) / source_width, (height - 2 * margin - 24) / source_height)

        def point(x: float, y: float) -> tuple[float, float]:
            px = margin + (x - min_x) * scale
            py = margin + (y - min_y) * scale
            return px, py

        for item in rectangles:
            x1, y1 = point(item.x1, item.y1)
            x2, y2 = point(item.x2, item.y2)
            dash = ' stroke-dasharray="5 4"' if item.layer == "F.CrtYd" else ""
            opacity = "0.65" if item.layer == "F.CrtYd" else "1"
            shapes.append(
                f'<rect x="{min(x1, x2):.2f}" y="{min(y1, y2):.2f}" '
                f'width="{abs(x2 - x1):.2f}" height="{abs(y2 - y1):.2f}" '
                f'fill="none" stroke="currentColor" stroke-width="2" opacity="{opacity}"{dash}/>'
            )
    else:
        shapes.append(
            '<text x="130" y="96" text-anchor="middle" font-size="13">'
            'Keine unterstützte Footprint-Geometrie</text>'
        )

    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 210" role="img">',
            f'  <title>Footprint: {escape(name)}</title>',
            '  <rect x="1" y="1" width="258" height="208" rx="8" fill="none" stroke="currentColor" opacity="0.25"/>',
            *[f"  {shape}" for shape in shapes],
            f'  <text x="130" y="194" text-anchor="middle" font-size="12">{escape(name)}</text>',
            '</svg>',
            '',
        ]
    )


def generated_files(
    footprint_root: Path = FOOTPRINT_ROOT,
    output_root: Path = OUTPUT_ROOT,
) -> dict[Path, str]:
    files: dict[Path, str] = {}
    sources = sorted(footprint_root.glob("Z_*.pretty/*.kicad_mod"), key=lambda path: str(path).casefold())
    for source in sources:
        text = source.read_text(encoding="utf-8")
        name = footprint_name(text, source.stem)
        files[output_root / f"{name}.svg"] = render_svg(name, parse_rectangles(text))
    return files


def write_previews(files: dict[Path, str]) -> None:
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_previews(files: dict[Path, str], output_root: Path = OUTPUT_ROOT) -> bool:
    expected_paths = set(files)
    actual_paths = set(output_root.glob("*.svg")) if output_root.is_dir() else set()
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
            print(f"{len(files)} Footprintvorschauen sind aktuell.")
            return 0
        print("Die Footprintvorschauen fehlen oder sind nicht aktuell.", file=sys.stderr)
        return 1
    write_previews(files)
    print(f"{len(files)} Footprintvorschauen erzeugt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
