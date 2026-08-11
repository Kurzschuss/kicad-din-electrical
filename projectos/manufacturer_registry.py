"""Dateibasierte, verifizierte Hersteller-Stammdaten für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .identifiers import BusinessId, ObjectId
from .manufacturer import Manufacturer, ManufacturerStatus


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "data" / "manufacturers" / "manufacturers.json"
_ALLOWED_SOURCE_STATES = {"verified", "unverified"}


@dataclass(frozen=True, slots=True)
class ManufacturerRegistryEntry:
    manufacturer: Manufacturer
    catalog_name: str
    aliases: tuple[str, ...] = ()
    source_url: str | None = None
    source_status: str = "unverified"
    note: str | None = None

    @property
    def display_name(self) -> str:
        return self.manufacturer.short_name or self.manufacturer.name

    @property
    def search_names(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                (
                    self.catalog_name,
                    self.display_name,
                    self.manufacturer.name,
                    *self.aliases,
                )
            )
        )


def load_manufacturer_registry(path: Path = REGISTRY_PATH) -> tuple[ManufacturerRegistryEntry, ...]:
    """Lädt und validiert die kanonischen Hersteller-Stammdaten."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Herstellerregister benötigt schema_version 1.")

    raw_items = payload.get("manufacturers")
    if not isinstance(raw_items, list):
        raise ValueError("Herstellerregister benötigt eine manufacturers-Liste.")

    entries: list[ManufacturerRegistryEntry] = []
    seen_ids: set[str] = set()
    seen_catalog_names: set[str] = set()
    seen_search_names: dict[str, str] = {}

    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("Jeder Herstellereintrag muss ein Objekt sein.")

        manufacturer_id = BusinessId.parse(str(raw.get("manufacturer_id") or ""))
        catalog_name = str(raw.get("catalog_name") or "").strip()
        if not catalog_name:
            raise ValueError(f"{manufacturer_id}: catalog_name fehlt.")

        source_status = str(raw.get("source_status") or "unverified").strip().lower()
        if source_status not in _ALLOWED_SOURCE_STATES:
            raise ValueError(
                f"{manufacturer_id}: source_status muss verified oder unverified sein."
            )

        status_text = str(raw.get("status") or ManufacturerStatus.ACTIVE.value).strip().upper()
        try:
            status = ManufacturerStatus(status_text)
        except ValueError as exc:
            raise ValueError(f"{manufacturer_id}: unbekannter Herstellerstatus {status_text!r}.") from exc

        aliases_raw = raw.get("aliases") or []
        if not isinstance(aliases_raw, list):
            raise ValueError(f"{manufacturer_id}: aliases muss eine Liste sein.")
        aliases = tuple(
            dict.fromkeys(
                alias.strip() for alias in map(str, aliases_raw) if alias.strip()
            )
        )

        manufacturer = Manufacturer(
            object_id=ObjectId.parse(str(raw.get("object_id") or "")),
            manufacturer_id=manufacturer_id,
            name=str(raw.get("name") or ""),
            short_name=str(raw.get("short_name") or "") or None,
            country_code=str(raw.get("country_code") or "") or None,
            website=str(raw.get("website") or "") or None,
            support_url=str(raw.get("support_url") or "") or None,
            status=status,
        )
        entry = ManufacturerRegistryEntry(
            manufacturer=manufacturer,
            catalog_name=catalog_name,
            aliases=aliases,
            source_url=str(raw.get("source_url") or "") or None,
            source_status=source_status,
            note=str(raw.get("note") or "").strip() or None,
        )

        id_key = str(manufacturer.manufacturer_id)
        if id_key in seen_ids:
            raise ValueError(f"Doppelte manufacturer_id: {id_key}")
        seen_ids.add(id_key)

        catalog_key = catalog_name.casefold()
        if catalog_key in seen_catalog_names:
            raise ValueError(f"Doppelter catalog_name: {catalog_name}")
        seen_catalog_names.add(catalog_key)

        for search_name in entry.search_names:
            key = search_name.casefold()
            owner = seen_search_names.get(key)
            if owner is not None and owner != id_key:
                raise ValueError(
                    f"Hersteller-Suchname {search_name!r} ist sowohl {owner} als auch {id_key} zugeordnet."
                )
            seen_search_names[key] = id_key

        entries.append(entry)

    return tuple(sorted(entries, key=lambda item: item.display_name.casefold()))


def find_manufacturer_entry(
    name: str,
    entries: tuple[ManufacturerRegistryEntry, ...] | None = None,
) -> ManufacturerRegistryEntry | None:
    """Findet einen Hersteller über Katalogname, Kurzname, Rechtsname oder Alias."""
    normalized = name.strip().casefold()
    if not normalized:
        return None
    source = load_manufacturer_registry() if entries is None else entries
    for entry in source:
        if normalized in {candidate.casefold() for candidate in entry.search_names}:
            return entry
    return None
