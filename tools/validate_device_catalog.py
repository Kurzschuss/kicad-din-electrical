#!/usr/bin/env python3
"""Validiert den herstellerneutralen Gerätekatalog ohne externe Abhängigkeiten."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
DEVICE_ROOT = REPO_ROOT / "data" / "devices"
SYMBOL_ROOT = REPO_ROOT / "symbols"
FOOTPRINT_ROOT = REPO_ROOT / "footprints"
TAXONOMY_PATH = REPO_ROOT / "data" / "taxonomy" / "device_families.json"

REQUIRED_FIELDS = {
    "id", "manufacturer", "series", "part_number", "device_type",
    "function_group", "symbol", "footprint_policy",
}
ALLOWED_FIELDS = REQUIRED_FIELDS | {
    "description", "poles", "rated_current_a", "residual_current_ma",
    "rcd_type", "trip_curve", "breaking_capacity_ka",
    "rated_short_circuit_current_ka", "making_breaking_capacity_ka",
    "modules", "footprint", "datasheet", "source_status", "name_de",
    "name_en", "abbreviation", "main_contacts_no", "main_contacts_nc",
    "utilization_category",
}
POLICIES = {"required", "optional", "none"}
SOURCE_STATES = {"template", "verified", "unverified"}
QUALIFIED_ID = re.compile(r"^[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+$")
DEVICE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]+$")
FAMILY_ID = re.compile(r"^[a-z0-9][a-z0-9._-]+$")
ABBREVIATION = re.compile(r"^[A-Z][A-Z0-9+_-]*$")


def load_device(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Wurzelelement muss ein Objekt sein")
    return data


def load_family_ids(path: Path = TAXONOMY_PATH) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    families = data.get("families") if isinstance(data, dict) else None
    if not isinstance(families, list):
        raise ValueError("Taxonomie muss eine Liste 'families' enthalten")
    result: set[str] = set()
    for item in families:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Jede Gerätefamilie benötigt eine Text-ID")
        family_id = item["id"]
        if not FAMILY_ID.fullmatch(family_id):
            raise ValueError(f"Ungültige Gerätefamilien-ID: {family_id}")
        if family_id in result:
            raise ValueError(f"Doppelte Gerätefamilien-ID: {family_id}")
        result.add(family_id)
    return result


def symbol_exists(qualified_id: str, symbol_root: Path = SYMBOL_ROOT) -> bool:
    library, symbol = qualified_id.split(":", 1)
    path = symbol_root / f"{library}.kicad_sym"
    return path.is_file() and f'(symbol "{symbol}"' in path.read_text(encoding="utf-8")


def footprint_exists(qualified_id: str, footprint_root: Path = FOOTPRINT_ROOT) -> bool:
    library, footprint = qualified_id.split(":", 1)
    return (footprint_root / f"{library}.pretty" / f"{footprint}.kicad_mod").is_file()


def validate_device(
    data: dict[str, object], *, symbol_root: Path = SYMBOL_ROOT,
    footprint_root: Path = FOOTPRINT_ROOT,
    allowed_families: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append("Fehlende Pflichtfelder: " + ", ".join(missing))
    unknown = sorted(data.keys() - ALLOWED_FIELDS)
    if unknown:
        errors.append("Unbekannte Felder: " + ", ".join(unknown))

    device_id = data.get("id")
    if not isinstance(device_id, str) or not DEVICE_ID.fullmatch(device_id):
        errors.append("id besitzt ein ungültiges Format")

    for field in ("manufacturer", "series", "part_number", "device_type", "function_group"):
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} muss ein nichtleerer Text sein")

    bilingual_fields = ("name_de", "name_en", "abbreviation")
    present_bilingual_fields = [field for field in bilingual_fields if field in data]
    if present_bilingual_fields and len(present_bilingual_fields) != len(bilingual_fields):
        missing_bilingual = sorted(set(bilingual_fields) - data.keys())
        errors.append(
            "Zweisprachige Metadaten sind unvollständig; fehlend: "
            + ", ".join(missing_bilingual)
        )
    for field in ("name_de", "name_en"):
        if field in data and (not isinstance(data[field], str) or not data[field].strip()):
            errors.append(f"{field} muss ein nichtleerer Text sein")
    abbreviation = data.get("abbreviation")
    if abbreviation is not None and (
        not isinstance(abbreviation, str) or not ABBREVIATION.fullmatch(abbreviation)
    ):
        errors.append("abbreviation muss ein etabliertes großgeschriebenes Fachkürzel sein")

    for field in ("rcd_type", "utilization_category"):
        value = data.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{field} muss ein nichtleerer Text sein")

    family = data.get("function_group")
    if isinstance(family, str) and allowed_families is not None and family not in allowed_families:
        errors.append(f"Unbekannte Gerätefamilie: {family}")

    symbol = data.get("symbol")
    if not isinstance(symbol, str) or not QUALIFIED_ID.fullmatch(symbol):
        errors.append("symbol muss eine qualifizierte Bibliotheks-ID sein")
    elif not symbol_exists(symbol, symbol_root):
        errors.append(f"Symbol existiert nicht: {symbol}")

    policy = data.get("footprint_policy")
    if policy not in POLICIES:
        errors.append("footprint_policy muss required, optional oder none sein")
    footprint = data.get("footprint")
    if footprint is not None:
        if not isinstance(footprint, str) or not QUALIFIED_ID.fullmatch(footprint):
            errors.append("footprint muss eine qualifizierte Bibliotheks-ID sein")
        elif not footprint_exists(footprint, footprint_root):
            errors.append(f"Footprint existiert nicht: {footprint}")
    if policy == "required" and not footprint:
        errors.append("footprint_policy required verlangt einen Footprint")
    if policy == "none" and footprint:
        errors.append("footprint_policy none darf keinen Footprint besitzen")

    source_status = data.get("source_status")
    if source_status is not None and source_status not in SOURCE_STATES:
        errors.append("source_status ist ungültig")
    value = data.get("poles")
    if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
        errors.append("poles muss eine positive ganze Zahl sein")
    for field in ("main_contacts_no", "main_contacts_nc"):
        value = data.get(field)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 1
        ):
            errors.append(f"{field} muss eine positive ganze Zahl sein")
    for field in (
        "rated_current_a",
        "residual_current_ma",
        "breaking_capacity_ka",
        "rated_short_circuit_current_ka",
        "making_breaking_capacity_ka",
        "modules",
    ):
        value = data.get(field)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0
        ):
            errors.append(f"{field} muss eine positive Zahl sein")
    return errors


def catalog_files(device_root: Path = DEVICE_ROOT) -> list[Path]:
    return sorted(path for path in device_root.rglob("*.yaml") if "schema" not in path.parts)


def validate_catalog(
    device_root: Path = DEVICE_ROOT, *, symbol_root: Path = SYMBOL_ROOT,
    footprint_root: Path = FOOTPRINT_ROOT, taxonomy_path: Path = TAXONOMY_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        allowed_families = load_family_ids(taxonomy_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"Gerätefamilien-Taxonomie kann nicht gelesen werden: {exc}"]

    seen_ids: dict[str, Path] = {}
    for path in catalog_files(device_root):
        try:
            data = load_device(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path}: Datei kann nicht gelesen werden: {exc}")
            continue
        for message in validate_device(
            data, symbol_root=symbol_root, footprint_root=footprint_root,
            allowed_families=allowed_families,
        ):
            errors.append(f"{path}: {message}")
        device_id = data.get("id")
        if isinstance(device_id, str):
            previous = seen_ids.get(device_id)
            if previous is not None:
                errors.append(f"{path}: Doppelte Geräte-ID, bereits in {previous}")
            else:
                seen_ids[device_id] = path
    return errors


def main() -> int:
    errors = validate_catalog()
    print(f"Gerätekatalog: {len(catalog_files())} Gerätedatei(en)")
    if not errors:
        print(f"Gerätefamilien: {len(load_family_ids())}")
        print("Fehler: 0")
        return 0
    print(f"Fehler: {len(errors)}", file=sys.stderr)
    for error in errors:
        print(f"[ERROR] {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
