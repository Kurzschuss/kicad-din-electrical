#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

KICAD_VERSION = "20231120"
QET_UNIT_MM = 0.254
FALLBACK_REFERENCE = "QET"
QET_COLLECTION_LICENSE = "CC-BY-3.0"


@dataclass
class ConversionStats:
    source_files: int = 0
    converted: int = 0
    zero_pin_symbols: int = 0
    symbols_with_adjustments: int = 0
    generated_pin_numbers: int = 0
    fallback_references: int = 0
    duplicate_names_resolved: int = 0
    missing_german_names: int = 0
    missing_german_name_paths: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    unsupported_nodes: Counter = field(default_factory=Counter)
    adjustment_counts: Counter = field(default_factory=Counter)

    def as_dict(self) -> dict:
        d = {
            "source_files": self.source_files,
            "converted": self.converted,
            "zero_pin_symbols": self.zero_pin_symbols,
            "symbols_with_adjustments": self.symbols_with_adjustments,
            "generated_pin_numbers": self.generated_pin_numbers,
            "fallback_references": self.fallback_references,
            "duplicate_names_resolved": self.duplicate_names_resolved,
            "missing_german_names": self.missing_german_names,
            "missing_german_name_paths": self.missing_german_name_paths,
            "errors": self.errors,
        }
        d["unsupported_nodes"] = dict(sorted(self.unsupported_nodes.items()))
        d["adjustment_counts"] = dict(sorted(self.adjustment_counts.items()))
        return d


def quote(value: object) -> str:
    s = "" if value is None else str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
    return f'"{s}"'


def num(value: float) -> str:
    if abs(value) < 5e-7:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def mm(value: object) -> float:
    try:
        return float(value or 0) * QET_UNIT_MM
    except (TypeError, ValueError):
        return 0.0


def xy(x: object, y: object) -> tuple[float, float]:
    return mm(x), -mm(y)


def token(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ._+-]+", "_", text.strip())
    return re.sub(r"_+", "_", text).strip("_") or "unnamed"


def internal_name(source_rel: Path) -> str:
    return "Z_Q_" + "__".join(token(x) for x in source_rel.with_suffix("").parts)


def humanize(part: str) -> str:
    return re.sub(r"^\d+[_-]?", "", part).replace("_", " ").replace("-", " ").strip()


def parse_style(style: str | None) -> dict[str, str]:
    out = {}
    for item in (style or "").split(";"):
        if ":" in item:
            k, v = item.split(":", 1)
            out[k.strip().lower()] = v.strip().lower()
    return out


def style_expr(style: str | None, adjustments: set[str]) -> tuple[str, str]:
    p = parse_style(style)
    ls = p.get("line-style", "normal")
    lw = p.get("line-weight", "normal")
    fi = p.get("filling", "none")
    line_types = {
        "normal": "default", "solid": "default", "dashed": "dash", "dash": "dash",
        "dotted": "dot", "dot": "dot", "dashdotted": "dash_dot",
        "dash-dot": "dash_dot", "dashdot": "dash_dot",
    }
    widths = {"none": 0.0, "thin": 0.127, "normal": 0.254,
              "thick": 0.508, "strong": 0.508, "high": 0.762}
    fills = {"none": "none", "black": "outline", "foreground": "outline",
             "color": "outline", "white": "background", "background": "background"}
    if ls not in line_types:
        adjustments.add(f"line_style_approximated:{ls}")
    if lw not in widths:
        adjustments.add(f"line_weight_approximated:{lw}")
    if fi not in fills:
        adjustments.add(f"fill_style_approximated:{fi}")
    stroke = f"(stroke (width {num(widths.get(lw, 0.254))}) (type {line_types.get(ls, 'default')}))"
    fill = f"(fill (type {fills.get(fi, 'none')}))"
    return stroke, fill


def font_size(font: str | None) -> float:
    if font:
        parts = [p.strip() for p in font.split(",")]
        if len(parts) > 1:
            try:
                pt = abs(float(parts[1]))
                if pt:
                    return min(5.08, max(0.635, pt * QET_UNIT_MM))
            except ValueError:
                pass
    return 1.27


def prop(name: str, value: str, y: float, hide: bool = True) -> str:
    hidden = " (hide yes)" if hide else ""
    return f'    (property {quote(name)} {quote(value)} (at 0 {num(y)} 0) (effects (font (size 1.27 1.27)){hidden}))'


def parse_names(root: ET.Element, fallback: str) -> dict[str, str]:
    names = {}
    node = root.find("names")
    if node is not None:
        for n in node.findall("name"):
            lang, value = (n.get("lang") or "").strip(), (n.text or "").strip()
            if lang and value:
                names[lang] = value
    if not names:
        names["de"] = fallback
    return names


def parse_information(text: str | None) -> tuple[str, str, str]:
    author, license_text, other = "", "", []
    for line in (text or "").splitlines():
        s = line.strip()
        m = re.match(r"(?i)^author\s*:\s*(.+)$", s)
        if m:
            author = m.group(1).strip()
            continue
        m = re.match(r"(?i)^licen[sc]e\s*:\s*(.+)$", s)
        if m:
            license_text = m.group(1).strip()
            continue
        if s:
            other.append(s)
    return author, license_text, " | ".join(other)


def parse_prefix_tree(labels_file: Path) -> dict[tuple[str, ...], str]:
    root = ET.parse(labels_file).getroot()
    out: dict[tuple[str, ...], str] = {}

    def walk(node: ET.Element, path: tuple[str, ...]):
        name = (node.get("name") or "").strip()
        if not name:
            return
        path = path + (name,)
        p = node.find("prefix")
        if p is not None and (p.text or "").strip():
            out[path] = (p.text or "").strip()
        for child in node.findall("category"):
            walk(child, path)

    for node in root.findall("category"):
        walk(node, ())
    return out


def prefix_for_category(parts: Sequence[str], prefixes: dict[tuple[str, ...], str]) -> str:
    candidates = [tuple(parts)]
    if parts:
        candidates.append(tuple(parts[1:]))
    best, best_depth = "", -1
    for candidate in candidates:
        found = ""
        for i in range(1, len(candidate) + 1):
            value = prefixes.get(candidate[:i])
            if value:
                found = value
                if i > best_depth:
                    best, best_depth = found, i
    return best


def explicit_label(root: ET.Element, description: ET.Element | None) -> str:
    for cname in ("elementInformations", "element_informations"):
        c = root.find(cname)
        if c is not None:
            for n in list(c):
                if (n.get("name") or "").strip().lower() == "label":
                    v = (n.text or n.get("text") or "").strip()
                    if v and v != "_":
                        return v
    if description is not None:
        for n in description.iter():
            if (n.get("tagg") or n.get("tag") or "").strip().lower() == "label":
                v = (n.get("text") or n.text or "").strip()
                if v and v != "_":
                    return v
            if n.tag == "dynamic_text" and n.findtext("info_name", "").strip().lower() == "label":
                v = n.findtext("text", "").strip()
                if v and v != "_":
                    return v
    return ""


def terminal_numbers(terminals: list[ET.Element]) -> tuple[list[str], int]:
    seen, out, generated, next_int = set(), [], 0, 1
    for t in terminals:
        v = (t.get("name") or "").strip()
        if not v or v in seen:
            while str(next_int) in seen:
                next_int += 1
            v, next_int, generated = str(next_int), next_int + 1, generated + 1
        seen.add(v)
        out.append(v)
    return out, generated


def pin_angle(orientation: str | None) -> int:
    return {"n": 270, "e": 180, "s": 90, "w": 0}.get((orientation or "").lower(), 0)


def poly(points: list[tuple[float, float]], style: str | None, adjustments: set[str]) -> str:
    stroke, fill = style_expr(style, adjustments)
    pts = " ".join(f"(xy {num(x)} {num(y)})" for x, y in points)
    return f"      (polyline (pts {pts}) {stroke} {fill})"


def polygon_points(node: ET.Element) -> list[tuple[float, float]]:
    coords: dict[int, dict[str, float]] = {}
    for key, value in node.attrib.items():
        m = re.fullmatch(r"([xy])(\d+)", key)
        if m:
            try:
                coords.setdefault(int(m.group(2)), {})[m.group(1)] = float(value)
            except ValueError:
                pass
    return [xy(v["x"], v["y"]) for _, v in sorted(coords.items()) if "x" in v and "y" in v]


def ellipse_points(x: float, y: float, w: float, h: float, steps: int = 48):
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    return [xy(cx + rx * math.cos(2 * math.pi * i / steps),
               cy + ry * math.sin(2 * math.pi * i / steps))
            for i in range(steps + 1)]


def arc_points(node: ET.Element):
    x, y = float(node.get("x", 0)), float(node.get("y", 0))
    w, h = float(node.get("width", 0)), float(node.get("height", 0))
    start, span = float(node.get("start", 0)), float(node.get("angle", 0))
    count = max(4, min(96, int(abs(span) / 7.5) + 1))
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    return [xy(cx + rx * math.cos(math.radians(start + span * i / count)),
               cy + ry * math.sin(math.radians(start + span * i / count)))
            for i in range(count + 1)]


def graphics(node: ET.Element, adjustments: set[str], unsupported: Counter) -> list[str]:
    tag, style = node.tag, node.get("style")
    out: list[str] = []
    if tag == "line":
        out.append(poly([xy(node.get("x1"), node.get("y1")), xy(node.get("x2"), node.get("y2"))], style, adjustments))
        if (node.get("end1") or "none") != "none" or (node.get("end2") or "none") != "none":
            adjustments.add("line_endpoint_decoration_omitted")
    elif tag in {"rect", "rectangle"}:
        x, y = float(node.get("x", 0)), float(node.get("y", 0))
        w, h = float(node.get("width", 0)), float(node.get("height", 0))
        if any(node.get(k) for k in ("rx", "ry", "radius")):
            adjustments.add("rounded_rectangle_approximated")
        stroke, fill = style_expr(style, adjustments)
        a, b = xy(x, y), xy(x + w, y + h)
        out.append(f"      (rectangle (start {num(a[0])} {num(a[1])}) (end {num(b[0])} {num(b[1])}) {stroke} {fill})")
    elif tag == "circle":
        x, y, d = float(node.get("x", 0)), float(node.get("y", 0)), float(node.get("diameter", 0))
        stroke, fill = style_expr(style, adjustments)
        cx, cy = xy(x + d / 2, y + d / 2)
        out.append(f"      (circle (center {num(cx)} {num(cy)}) (radius {num(mm(d) / 2)}) {stroke} {fill})")
    elif tag == "ellipse":
        x, y = float(node.get("x", 0)), float(node.get("y", 0))
        w, h = float(node.get("width", 0)), float(node.get("height", 0))
        if abs(w - h) < 1e-9:
            stroke, fill = style_expr(style, adjustments)
            cx, cy = xy(x + w / 2, y + h / 2)
            out.append(f"      (circle (center {num(cx)} {num(cy)}) (radius {num(mm(w) / 2)}) {stroke} {fill})")
        else:
            out.append(poly(ellipse_points(x, y, w, h), style, adjustments))
            adjustments.add("ellipse_approximated")
    elif tag == "arc":
        out.append(poly(arc_points(node), style, adjustments))
        adjustments.add("arc_approximated")
    elif tag == "polygon":
        pts = polygon_points(node)
        if len(pts) >= 2:
            if (node.get("closed") or "true").lower() != "false" and pts[0] != pts[-1]:
                pts.append(pts[0])
            out.append(poly(pts, style, adjustments))
        else:
            adjustments.add("polygon_without_enough_points")
    elif tag == "text":
        text = (node.get("text") or node.text or "").strip()
        if text:
            x, y = xy(node.get("x"), node.get("y"))
            r = -float(node.get("rotation", 0) or 0)
            fs = font_size(node.get("font"))
            out.append(f"      (text {quote(text)} (at {num(x)} {num(y)} {num(r)}) (effects (font (size {num(fs)} {num(fs)}))))")
    elif tag == "dynamic_text":
        info = node.findtext("info_name", "").strip()
        text = node.findtext("text", "").strip()
        if info.lower() == "label":
            pass
        elif text and text != "_":
            x, y = xy(node.get("x"), node.get("y"))
            r = -float(node.get("rotation", 0) or 0)
            fs = font_size(node.get("font"))
            out.append(f"      (text {quote(text)} (at {num(x)} {num(y)} {num(r)}) (effects (font (size {num(fs)} {num(fs)}))))")
        elif (node.get("text_from") or "").lower() not in {"", "usertext"}:
            adjustments.add(f"dynamic_text_omitted:{info or node.get('text_from')}")
    elif tag != "terminal":
        unsupported[tag] += 1
        adjustments.add(f"unsupported_node:{tag}")
    return out


def bounds(description: ET.Element | None) -> tuple[float, float]:
    ys = []
    if description is not None:
        for n in description.iter():
            for a in ("y", "y1", "y2"):
                if a in n.attrib:
                    try:
                        ys.append(-float(n.attrib[a]) * QET_UNIT_MM)
                    except ValueError:
                        pass
            if "y" in n.attrib and "height" in n.attrib:
                try:
                    ys.append(-(float(n.attrib["y"]) + float(n.attrib["height"])) * QET_UNIT_MM)
                except ValueError:
                    pass
    return max(ys, default=0.0), min(ys, default=0.0)


def keywords(names: dict[str, str], rel: Path, reference: str) -> str:
    items = [names.get("de", ""), names.get("en", ""), rel.stem.replace("_", " ")]
    items += [humanize(x) for x in rel.parent.parts]
    if reference != FALLBACK_REFERENCE:
        items.append(reference)
    seen, out = set(), []
    for item in items:
        item = " ".join(item.split())
        if item and item.casefold() not in seen:
            seen.add(item.casefold())
            out.append(item)
    return " ".join(out)


def convert_element(source_file: Path, source_root: Path, prefixes, stats: ConversionStats, used: set[str]) -> str:
    root = ET.parse(source_file).getroot()
    if root.tag != "definition":
        raise ValueError(f"unexpected root tag: {root.tag}")
    rel = source_file.relative_to(source_root)
    collection = source_root.name
    source_path = str(Path(collection) / rel).replace("\\", "/")
    names = parse_names(root, rel.stem.replace("_", " "))
    display = names.get("de") or names.get("en") or next(iter(names.values()))
    description = root.find("description")
    adjustments: set[str] = set()
    if not names.get("de"):
        fallback = "en" if names.get("en") else "other"
        adjustments.add(f"german_name_fallback:{fallback}")
        stats.missing_german_names += 1
        stats.missing_german_name_paths.append(source_path)
    terminals = [] if description is None else list(description.findall("terminal"))
    numbers, generated = terminal_numbers(terminals)
    stats.generated_pin_numbers += generated
    if generated:
        adjustments.add("generated_pin_number")
    category_parts = (collection,) + rel.parent.parts
    category = " / ".join(category_parts)
    reference = explicit_label(root, description) or prefix_for_category(category_parts, prefixes)
    if not reference:
        reference = FALLBACK_REFERENCE
        adjustments.add("reference_prefix_missing:qet_placeholder")
        stats.fallback_references += 1
    name = internal_name(rel)
    if name in used:
        name += "__" + hashlib.sha1(str(rel).encode()).hexdigest()[:8]
        stats.duplicate_names_resolved += 1
    used.add(name)
    author, license_text, other = parse_information(root.findtext("informations"))
    drawing = []
    if description is not None:
        for n in list(description):
            drawing += graphics(n, adjustments, stats.unsupported_nodes)
    if other:
        adjustments.add("qet_information_preserved_unstructured")
    if not terminals:
        stats.zero_pin_symbols += 1
    if adjustments:
        stats.symbols_with_adjustments += 1
        stats.adjustment_counts.update(adjustments)
    top, bottom = bounds(description)
    hidden_ref = not terminals
    uuid_node = root.find("uuid")
    uuid = uuid_node.get("uuid") if uuid_node is not None else ""
    props = [
        prop("Reference", reference, top + 2.54, hidden_ref),
        prop("Value", display, top + 5.08, False),
        prop("Footprint", "", bottom - 2.54),
        prop("Datasheet", "", bottom - 3.81),
        prop("Description", f"{display} | QET-Kategorie: {category}", bottom - 5.08),
        prop("QET_Category", category, bottom - 6.35),
        prop("QET_Source_Path", source_path, bottom - 7.62),
        prop("QET_Author", author, bottom - 8.89),
        prop("QET_License", license_text, bottom - 10.16),
        prop("QET_Collection_License", QET_COLLECTION_LICENSE, bottom - 11.43),
        prop("QET_Original_Pin_Count", str(len(terminals)), bottom - 12.70),
        prop("QET_Adjustments", "; ".join(sorted(adjustments)) if adjustments else "none", bottom - 13.97),
        prop("QET_Informations", other, bottom - 15.24),
        prop("QET_UUID", uuid, bottom - 16.51),
        prop("ki_keywords", keywords(names, rel, reference), bottom - 17.78),
    ]
    out = [
        f"  (symbol {quote(name)}",
        "    (pin_names (offset 0))",
        "    (exclude_from_sim no)",
        f"    (in_bom {'yes' if terminals else 'no'})",
        f"    (on_board {'yes' if terminals else 'no'})",
        *props,
        f"    (symbol {quote(name + '_0_1')}",
        *drawing,
        "    )",
    ]
    if terminals:
        out.append(f"    (symbol {quote(name + '_1_1')}")
        for terminal, number in zip(terminals, numbers):
            x, y = xy(terminal.get("x"), terminal.get("y"))
            out.append(
                f"      (pin passive line (at {num(x)} {num(y)} {pin_angle(terminal.get('orientation'))}) "
                f"(length {num(QET_UNIT_MM)}) (name \"~\" (effects (font (size 1 1)))) "
                f"(number {quote(number)} (effects (font (size 1 1)))))"
            )
        out.append("    )")
    out.append("  )")
    stats.converted += 1
    return "\n".join(out)


def discover_files(source_root: Path, scopes: Sequence[str]) -> list[Path]:
    files = []
    for scope in scopes:
        root = source_root / scope
        if not root.is_dir():
            raise FileNotFoundError(f"QET scope not found: {root}")
        files += list(root.rglob("*.elmt"))
    return sorted(set(files), key=lambda x: x.as_posix().casefold())


def convert_library(source_root: Path, labels_file: Path | None, scopes: Sequence[str], output_file: Path, report_file: Path | None = None) -> ConversionStats:
    stats = ConversionStats()
    files = discover_files(source_root, scopes)
    stats.source_files = len(files)
    prefixes = parse_prefix_tree(labels_file) if labels_file is not None and labels_file.is_file() else {}
    used, symbols = set(), []
    for file in files:
        try:
            symbols.append(convert_element(file, source_root, prefixes, stats, used))
        except Exception as exc:
            stats.errors.append({
                "path": str(Path(source_root.name) / file.relative_to(source_root)).replace("\\", "/"),
                "error": f"{type(exc).__name__}: {exc}",
            })
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        f"(kicad_symbol_lib (version {KICAD_VERSION}) (generator qet_to_kicad)\n"
        + "\n".join(symbols) + "\n)\n",
        encoding="utf-8", newline="\n",
    )
    report = stats.as_dict() | {
        "scopes": list(scopes),
        "source_root": str(source_root),
        "labels_file": str(labels_file) if labels_file is not None else None,
        "output_file": str(output_file),
    }
    if report_file is not None:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stats


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qet-root", type=Path, required=True)
    ap.add_argument("--labels", type=Path)
    ap.add_argument("--scope", action="append", dest="scopes")
    ap.add_argument("--output", type=Path, default=Path("symbols/Z_Q_QElectroTech.kicad_sym"))
    ap.add_argument("--report", type=Path, default=Path("build/qet-conversion-report.json"))
    ap.add_argument("--fail-on-errors", action="store_true")
    args = ap.parse_args(argv)
    labels_file = args.labels
    if labels_file is None:
        candidate = args.qet_root / "qet_labels.xml"
        labels_file = candidate if candidate.is_file() else None
    scopes = args.scopes
    if not scopes:
        scopes = sorted(path.name for path in args.qet_root.iterdir() if path.is_dir())
    stats = convert_library(
        args.qet_root,
        labels_file,
        scopes,
        args.output,
        args.report,
    )
    print(json.dumps(stats.as_dict(), ensure_ascii=False, indent=2))
    if args.fail_on_errors and stats.errors:
        return 2
    return 0 if stats.converted == stats.source_files else 3


if __name__ == "__main__":
    raise SystemExit(main())
