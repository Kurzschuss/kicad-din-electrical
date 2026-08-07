"""Fachliches Domänenmodell des ProjectOS-Gerätekatalogs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
import re

from .identifiers import BusinessId, ObjectId

_PROPERTY_KEY = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class DeviceCategory(StrEnum):
    MCB = "MCB"
    RCCB = "RCCB"
    RCBO = "RCBO"
    AFDD = "AFDD"
    SPD = "SPD"
    CONTACTOR = "CONTACTOR"
    RELAY = "RELAY"
    OTHER = "OTHER"


class CatalogDeviceStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


@dataclass(frozen=True, slots=True)
class DeviceProperty:
    """Typunabhängige, normalisierte Eigenschaft eines Kataloggeräts."""

    key: str
    value: str
    unit: str | None = None

    def __post_init__(self) -> None:
        key = self.key.strip().lower()
        value = self.value.strip()
        unit = self.unit.strip() if self.unit is not None else None
        if not _PROPERTY_KEY.fullmatch(key):
            raise ValueError("Eigenschaftsschlüssel müssen snake_case verwenden.")
        if not value:
            raise ValueError("Eine Geräteeigenschaft benötigt einen Wert.")
        if unit == "":
            unit = None
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "unit", unit)


@dataclass(frozen=True, slots=True)
class CatalogDevice:
    """Aggregate Root eines herstellerunabhängigen Gerätekatalogeintrags."""

    object_id: ObjectId
    catalog_id: BusinessId
    name: str
    category: DeviceCategory
    description: str = ""
    properties: tuple[DeviceProperty, ...] = ()
    tags: frozenset[str] = frozenset()
    status: CatalogDeviceStatus = CatalogDeviceStatus.DRAFT
    revision: int = 0

    def __post_init__(self) -> None:
        name = self.name.strip()
        description = self.description.strip()
        properties = tuple(self.properties)
        tags = frozenset(tag.strip().lower() for tag in self.tags if tag.strip())
        if not name:
            raise ValueError("Ein Kataloggerät benötigt einen Namen.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        keys = tuple(item.key for item in properties)
        if len(keys) != len(set(keys)):
            raise ValueError("Eigenschaftsschlüssel müssen innerhalb eines Geräts eindeutig sein.")
        if self.status is CatalogDeviceStatus.ACTIVE and not properties:
            raise ValueError("Ein aktives Kataloggerät benötigt mindestens eine technische Eigenschaft.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "properties", properties)
        object.__setattr__(self, "tags", tags)

    def set_property(self, device_property: DeviceProperty) -> "CatalogDevice":
        """Ersetzt eine gleichnamige Eigenschaft oder fügt sie deterministisch hinzu."""
        values = {item.key: item for item in self.properties}
        values[device_property.key] = device_property
        ordered = tuple(values[key] for key in sorted(values))
        return replace(self, properties=ordered, revision=self.revision + 1)

    def remove_property(self, key: str) -> "CatalogDevice":
        normalized = key.strip().lower()
        remaining = tuple(item for item in self.properties if item.key != normalized)
        if len(remaining) == len(self.properties):
            raise LookupError("ERR-CAT-0001: Geräteeigenschaft wurde nicht gefunden.")
        if self.status is CatalogDeviceStatus.ACTIVE and not remaining:
            raise ValueError("ERR-CAT-0002: Die letzte Eigenschaft eines aktiven Geräts darf nicht entfernt werden.")
        return replace(self, properties=remaining, revision=self.revision + 1)

    def activate(self) -> "CatalogDevice":
        if self.status is CatalogDeviceStatus.RETIRED:
            raise ValueError("ERR-CAT-0003: Ein ausgemustertes Gerät kann nicht erneut aktiviert werden.")
        if not self.properties:
            raise ValueError("ERR-CAT-0004: Ein Gerät ohne technische Eigenschaften kann nicht aktiviert werden.")
        if self.status is CatalogDeviceStatus.ACTIVE:
            return self
        return replace(self, status=CatalogDeviceStatus.ACTIVE, revision=self.revision + 1)

    def retire(self) -> "CatalogDevice":
        if self.status is CatalogDeviceStatus.RETIRED:
            return self
        return replace(self, status=CatalogDeviceStatus.RETIRED, revision=self.revision + 1)

    def rename(self, name: str) -> "CatalogDevice":
        normalized = name.strip()
        if not normalized:
            raise ValueError("Ein Kataloggerät benötigt einen Namen.")
        if normalized == self.name:
            return self
        return replace(self, name=normalized, revision=self.revision + 1)
