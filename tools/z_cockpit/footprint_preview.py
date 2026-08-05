from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from tools.validate_device_catalog import REPO_ROOT
from .symbol_preview import parse_symbol_reference


@dataclass(frozen=True)
class FootprintAssignment:
    symbol_reference: str
    symbol_name: str
    footprint_name: str | None
    footprint_file: Path | None
    mapped: bool
    footprint_available: bool
    preview_available: bool


def load_footprint_mapping(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    """Liest die zentrale Symbol-zu-Footprint-Zuordnung."""
    mapping_file = repo_root / "metadata" / "footprint_mapping.csv"
    if not mapping_file.is_file():
        return {}
    with mapping_file.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        if rows.fieldnames != ["Symbol", "Footprint"]:
            raise ValueError("footprint_mapping.csv benötigt die Spalten Symbol und Footprint")
        mapping: dict[str, str] = {}
        for row in rows:
            symbol = (row.get("Symbol") or "").strip()
            footprint = (row.get("Footprint") or "").strip()
            if not symbol or not footprint:
                raise ValueError("Leere Symbol- oder Footprint-Zuordnung")
            if symbol in mapping:
                raise ValueError(f"Doppelte Footprint-Zuordnung für {symbol}")
            mapping[symbol] = footprint
        return mapping


def footprint_assignment(reference: str, repo_root: Path = REPO_ROOT) -> FootprintAssignment:
    """Ermittelt Zuordnung und Dateistatus für eine Symbolreferenz."""
    _, symbol_name = parse_symbol_reference(reference)
    footprint_name = load_footprint_mapping(repo_root).get(symbol_name)
    if footprint_name is None:
        return FootprintAssignment(reference, symbol_name, None, None, False, False, False)

    footprint_file = (
        repo_root
        / "footprints"
        / f"{footprint_name}.pretty"
        / f"{footprint_name}.kicad_mod"
    )
    preview_file = (
        repo_root
        / "docs"
        / "site"
        / "footprint-previews"
        / f"{footprint_name}.svg"
    )
    return FootprintAssignment(
        symbol_reference=reference,
        symbol_name=symbol_name,
        footprint_name=footprint_name,
        footprint_file=footprint_file,
        mapped=True,
        footprint_available=footprint_file.is_file(),
        preview_available=preview_file.is_file(),
    )
