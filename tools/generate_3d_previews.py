#!/usr/bin/env python3
"""Erzeugt deterministische technische 3D-SVG-Vorschauen für KiCad-Footprints.

Die Vorschau unterscheidet bewusst zwischen echten KiCad-3D-Modellreferenzen
und einer rein aus vorhandener F.Fab-Geometrie extrudierten Hüllkörperansicht.
Eine Hüllkörperansicht wird nicht als vorhandenes 3D-Modell gewertet.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import sys

from tools.generate_footprint_previews import FootprintRectangle, footprint_name, parse_rectangles

REPO_ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = REPO_ROOT / "footprints"
OUTPUT_ROOT = REPO_ROOT / "docs" / "site" / "3d-previews"
MODEL_ROOT = REPO_ROOT / "3dmodels" / "Z_3DModell.3dshapes"
MODEL_RE = re.compile(r'\(model\s+"([^"]+)"')


@dataclass(frozen=True)
class ThreeDPreviewSource:
    footprint_name: str
    rectangles: tuple[FootprintRectangle, ...]
    model_reference: str | None
    model_file: Path | None
    model_available: bool

    @property
    def fab_rectangles(self) -> tuple[FootprintRectangle, ...]:
        return tuple(item for item in self.rectangles if item.layer == "F.Fab")

    @property
    def status(self) -> str:
        if self.model_reference and self.model_available:
            return "Modell"
        if self.model_reference:
            return "Modellreferenz fehlt"
        if self.fab_rectangles:
            return "Hüllkörper"
        return "Fehlt"

    @property
    def preview_available(self) -> bool:
        return self.status in {"Modell", "Hüllkörper"}


def parse_model_reference(text: str) -> str | None:
    match = MODEL_RE.search(text)
    return match.group(1).strip() if match else None


def resolve_model_reference(reference: str | None, repo_root: Path = REPO_ROOT) -> Path | None:
    """Löst ausschließlich Repository-eigene KICAD_Z_3DMODEL_DIR-Referenzen auf."""
    if not reference:
        return None
    normalized = reference.replace("\\", "/")
    prefixes = (
        "${KICAD_Z_3DMODEL_DIR}/",
        "$KICAD_Z_3DMODEL_DIR/",
    )
    for prefix in prefixes:
        if normalized.startswith(prefix):
            relative = normalized[len(prefix):]
            if not relative or ".." in Path(relative).parts:
                return None
            return repo_root / "3dmodels" / "Z_3DModell.3dshapes" / relative
    if normalized.startswith("3dmodels/Z_3DModell.3dshapes/"):
        relative = normalized.split("/", 2)[2]
        if not relative or ".." in Path(relative).parts:
            return None
        return repo_root / "3dmodels" / "Z_3DModell.3dshapes" / relative
    return None


def preview_source(path: Path, repo_root: Path = REPO_ROOT) -> ThreeDPreviewSource:
    text = path.read_text(encoding="utf-8")
    reference = parse_model_reference(text)
    model_file = resolve_model_reference(reference, repo_root)
    return ThreeDPreviewSource(
        footprint_name=footprint_name(text, path.stem),
        rectangles=tuple(parse_rectangles(text)),
        model_reference=reference,
        model_file=model_file,
        model_available=bool(model_file and model_file.is_file()),
    )


def _bounds(rectangles: tuple[FootprintRectangle, ...]) -> tuple[float, float, float, float]:
    xs = [value for item in rectangles for value in (item.x1, item.x2)]
    ys = [value for item in rectangles for value in (item.y1, item.y2)]
    return min(xs), min(ys), max(xs), max(ys)


def _projected_box(rectangles: tuple[FootprintRectangle, ...]) -> list[str]:
    min_x, min_y, max_x, max_y = _bounds(rectangles)
    source_w = max(max_x - min_x, 1.0)
    source_h = max(max_y - min_y, 1.0)
    max_source = max(source_w, source_h)
    scale = min(145.0 / source_w, 118.0 / source_h)
    w = source_w * scale
    h = source_h * scale
    depth = max(18.0, min(38.0, max_source * scale * 0.22))
    x = 130.0 - w / 2.0 - depth * 0.18
    y = 94.0 - h / 2.0 + depth * 0.20
    dx = depth * 0.72
    dy = -depth * 0.45
    front = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    back = tuple((px + dx, py + dy) for px, py in front)

    def points(items: tuple[tuple[float, float], ...]) -> str:
        return " ".join(f"{px:.2f},{py:.2f}" for px, py in items)

    top = (front[0], front[1], back[1], back[0])
    side = (front[1], front[2], back[2], back[1])
    return [
        f'<polygon points="{points(back)}" fill="none" stroke="currentColor" stroke-width="1.6" opacity="0.35"/>',
        f'<polygon points="{points(top)}" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-width="1.8"/>',
        f'<polygon points="{points(side)}" fill="currentColor" fill-opacity="0.05" stroke="currentColor" stroke-width="1.8"/>',
        f'<polygon points="{points(front)}" fill="none" stroke="currentColor" stroke-width="2.2"/>',
    ]


def render_svg(source: ThreeDPreviewSource) -> str:
    status = source.status
    shapes: list[str] = []
    fab = source.fab_rectangles
    if fab:
        shapes.extend(_projected_box(fab))
    elif source.model_available:
        shapes.extend(
            (
                '<path d="M78 117 L130 83 L182 117 L130 151 Z" fill="currentColor" fill-opacity="0.07" stroke="currentColor" stroke-width="2"/>',
                '<path d="M78 117 L78 72 L130 39 L130 83 Z" fill="currentColor" fill-opacity="0.04" stroke="currentColor" stroke-width="2"/>',
                '<path d="M130 83 L130 39 L182 72 L182 117 Z" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/>',
            )
        )
    else:
        shapes.append('<text x="130" y="92" text-anchor="middle" font-size="13">Keine 3D-Geometrie verfügbar</text>')

    model_name = Path(source.model_reference.replace("\\", "/")).name if source.model_reference else ""
    if status == "Modell":
        subtitle = f"KiCad-3D-Modell: {model_name}"
    elif status == "Modellreferenz fehlt":
        subtitle = f"3D-Modell nicht auflösbar: {model_name or source.model_reference}"
    elif status == "Hüllkörper":
        subtitle = "Technischer Hüllkörper aus F.Fab · keine Modelltiefe"
    else:
        subtitle = "Kein 3D-Modell und keine F.Fab-Hüllgeometrie"

    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 210" role="img">',
            f'  <title>3D-Vorschau: {escape(source.footprint_name)}</title>',
            '  <rect x="1" y="1" width="258" height="208" rx="8" fill="none" stroke="currentColor" opacity="0.25"/>',
            *[f"  {shape}" for shape in shapes],
            f'  <text x="130" y="177" text-anchor="middle" font-size="12" font-weight="600">{escape(source.footprint_name)}</text>',
            f'  <text x="130" y="194" text-anchor="middle" font-size="10">{escape(subtitle)}</text>',
            '</svg>',
            '',
        ]
    )


def generated_files(
    footprint_root: Path = FOOTPRINT_ROOT,
    output_root: Path = OUTPUT_ROOT,
    repo_root: Path = REPO_ROOT,
) -> dict[Path, str]:
    files: dict[Path, str] = {}
    sources = sorted(footprint_root.glob("Z_*.pretty/*.kicad_mod"), key=lambda path: str(path).casefold())
    for path in sources:
        source = preview_source(path, repo_root)
        files[output_root / f"{source.footprint_name}.svg"] = render_svg(source)
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
    parser.add_argument("--check", action="store_true", help="nur prüfen, ob alle 3D-Vorschauen aktuell sind")
    args = parser.parse_args()
    files = generated_files()
    if args.check:
        if check_previews(files):
            print(f"{len(files)} 3D-Vorschauen sind aktuell.")
            return 0
        print("Die 3D-Vorschauen fehlen oder sind nicht aktuell.", file=sys.stderr)
        return 1
    write_previews(files)
    print(f"{len(files)} 3D-Vorschauen erzeugt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
