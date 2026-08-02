#!/usr/bin/env python3
"""Erzeugt einzelne Gerätedateien aus parametrischen Serienbeschreibungen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SERIES_ROOT = REPO_ROOT / "data" / "device_series"
OUTPUT_ROOT = REPO_ROOT / "data" / "devices" / "generated"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]+$")


def load_series(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Wurzelelement muss ein Objekt sein")
    return data


def expand_series(data: dict[str, object]) -> list[dict[str, object]]:
    series_id = data.get("series_id")
    defaults = data.get("defaults")
    variants = data.get("variants")
    if not isinstance(series_id, str) or not ID_RE.fullmatch(series_id):
        raise ValueError("series_id besitzt ein ungültiges Format")
    if not isinstance(defaults, dict):
        raise ValueError("defaults muss ein Objekt sein")
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants muss eine nichtleere Liste sein")

    result: list[dict[str, object]] = []
    seen: set[str] = set()
    for variant in variants:
        if not isinstance(variant, dict):
            raise ValueError("jede Variante muss ein Objekt sein")
        variant_id = variant.get("variant_id")
        if not isinstance(variant_id, str) or not ID_RE.fullmatch(variant_id):
            raise ValueError("variant_id besitzt ein ungültiges Format")
        if variant_id in seen:
            raise ValueError(f"doppelte variant_id: {variant_id}")
        seen.add(variant_id)

        device = dict(defaults)
        device.update({key: value for key, value in variant.items() if key != "variant_id"})
        device["id"] = f"{series_id}.{variant_id}"
        result.append(device)
    return result


def generated_files(series_root: Path = SERIES_ROOT, output_root: Path = OUTPUT_ROOT) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for source in sorted(series_root.rglob("*.yaml"), key=lambda item: str(item).casefold()):
        data = load_series(source)
        series_id = str(data["series_id"])
        folder = output_root / series_id
        for device in expand_series(data):
            variant_id = str(device["id"]).rsplit(".", 1)[-1]
            target = folder / f"{variant_id}.yaml"
            files[target] = json.dumps(device, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return files


def write_files(files: dict[Path, str], output_root: Path = OUTPUT_ROOT) -> None:
    if output_root.is_dir():
        for path in output_root.rglob("*.yaml"):
            path.unlink()
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_files(files: dict[Path, str], output_root: Path = OUTPUT_ROOT) -> bool:
    actual = set(output_root.rglob("*.yaml")) if output_root.is_dir() else set()
    if actual != set(files):
        return False
    return all(path.read_text(encoding="utf-8") == content for path, content in files.items())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="nur Aktualität prüfen")
    args = parser.parse_args()
    try:
        files = generated_files()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Fehler in Geräteserie: {exc}", file=sys.stderr)
        return 1
    if args.check:
        if check_files(files):
            print(f"{len(files)} erzeugte Gerätevarianten sind aktuell.")
            return 0
        print("Die erzeugten Gerätevarianten fehlen oder sind nicht aktuell.", file=sys.stderr)
        return 1
    write_files(files)
    print(f"{len(files)} Gerätevarianten erzeugt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
