"""Herstellerprodukte, Artikelnummern und externe Produktkennungen."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
import re

from .identifiers import BusinessId, ObjectId
from .manufacturer import Manufacturer, ManufacturerStatus, ProductSeries


class ProductStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DISCONTINUED = "DISCONTINUED"


class ProductIdentifierType(StrEnum):
    MANUFACTURER_PART_NUMBER = "MANUFACTURER_PART_NUMBER"
    GTIN = "GTIN"
    EAN = "EAN"
    UPC = "UPC"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class ProductIdentifier:
    identifier_type: ProductIdentifierType
    value: str
    scheme: str | None = None

    def __post_init__(self) -> None:
        value = self.value.strip()
        scheme = self.scheme.strip().upper() if self.scheme else None
        if not value:
            raise ValueError("ERR-PRD-0001: Eine Produktkennung darf nicht leer sein.")
        if self.identifier_type in {ProductIdentifierType.GTIN, ProductIdentifierType.EAN, ProductIdentifierType.UPC}:
            if not value.isdigit():
                raise ValueError("ERR-PRD-0002: Numerische Handelskennungen dürfen nur Ziffern enthalten.")
            allowed_lengths = {
                ProductIdentifierType.GTIN: {8, 12, 13, 14},
                ProductIdentifierType.EAN: {8, 13},
                ProductIdentifierType.UPC: {12},
            }[self.identifier_type]
            if len(value) not in allowed_lengths:
                raise ValueError("ERR-PRD-0002: Die Länge der Handelskennung ist ungültig.")
        if self.identifier_type is ProductIdentifierType.OTHER and not scheme:
            raise ValueError("ERR-PRD-0003: Eine sonstige Produktkennung benötigt ein Schema.")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "scheme", scheme)


@dataclass(frozen=True, slots=True)
class ManufacturerProduct:
    object_id: ObjectId
    product_id: BusinessId
    catalog_device_id: BusinessId
    manufacturer_id: BusinessId
    name: str
    identifiers: tuple[ProductIdentifier, ...]
    series_id: BusinessId | None = None
    description: str = ""
    status: ProductStatus = ProductStatus.DRAFT
    revision: int = 0

    def __post_init__(self) -> None:
        name = self.name.strip()
        description = self.description.strip()
        identifiers = tuple(self.identifiers)
        if not name:
            raise ValueError("ERR-PRD-0004: Ein Herstellerprodukt benötigt einen Namen.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        _ensure_unique_identifier_types(identifiers)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "identifiers", identifiers)

    @classmethod
    def create(
        cls,
        *,
        object_id: ObjectId,
        product_id: BusinessId,
        catalog_device_id: BusinessId,
        manufacturer: Manufacturer,
        name: str,
        identifiers: tuple[ProductIdentifier, ...],
        series: ProductSeries | None = None,
        description: str = "",
    ) -> "ManufacturerProduct":
        if manufacturer.status is not ManufacturerStatus.ACTIVE:
            raise ValueError("ERR-PRD-0005: Ein Herstellerprodukt benötigt einen aktiven Hersteller.")
        if series is not None:
            if series.manufacturer_id != manufacturer.manufacturer_id:
                raise ValueError("ERR-PRD-0006: Die Produktserie gehört zu einem anderen Hersteller.")
            if not series.active:
                raise ValueError("ERR-PRD-0005: Ein Herstellerprodukt benötigt eine aktive Produktserie.")
        return cls(
            object_id=object_id,
            product_id=product_id,
            catalog_device_id=catalog_device_id,
            manufacturer_id=manufacturer.manufacturer_id,
            series_id=series.series_id if series else None,
            name=name,
            description=description,
            identifiers=identifiers,
        )

    def activate(self) -> "ManufacturerProduct":
        if self.status is ProductStatus.DISCONTINUED:
            raise ValueError("ERR-PRD-0007: Ein abgekündigtes Produkt darf nicht reaktiviert werden.")
        if not self.identifiers:
            raise ValueError("ERR-PRD-0008: Ein aktives Produkt benötigt mindestens eine Produktkennung.")
        if self.status is ProductStatus.ACTIVE:
            return self
        return replace(self, status=ProductStatus.ACTIVE, revision=self.revision + 1)

    def discontinue(self) -> "ManufacturerProduct":
        if self.status is ProductStatus.DISCONTINUED:
            return self
        return replace(self, status=ProductStatus.DISCONTINUED, revision=self.revision + 1)

    def with_identifier(self, identifier: ProductIdentifier) -> "ManufacturerProduct":
        remaining = tuple(item for item in self.identifiers if item.identifier_type is not identifier.identifier_type)
        return replace(self, identifiers=(*remaining, identifier), revision=self.revision + 1)

    def remove_identifier(self, identifier_type: ProductIdentifierType) -> "ManufacturerProduct":
        remaining = tuple(item for item in self.identifiers if item.identifier_type is not identifier_type)
        if len(remaining) == len(self.identifiers):
            raise ValueError("ERR-PRD-0009: Die Produktkennung wurde nicht gefunden.")
        if self.status is ProductStatus.ACTIVE and not remaining:
            raise ValueError("ERR-PRD-0010: Die letzte Kennung eines aktiven Produkts darf nicht entfernt werden.")
        return replace(self, identifiers=remaining, revision=self.revision + 1)


def ensure_unique_product_identifiers(
    existing: tuple[ManufacturerProduct, ...],
    candidate: ManufacturerProduct,
) -> None:
    candidate_keys = {_identifier_key(item) for item in candidate.identifiers}
    for product in existing:
        if product.product_id == candidate.product_id:
            continue
        collisions = candidate_keys & {_identifier_key(item) for item in product.identifiers}
        if collisions:
            raise ValueError("ERR-PRD-0011: Eine Produktkennung ist bereits einem anderen Produkt zugeordnet.")


def _ensure_unique_identifier_types(identifiers: tuple[ProductIdentifier, ...]) -> None:
    keys = [(_type_key(item)) for item in identifiers]
    if len(keys) != len(set(keys)):
        raise ValueError("ERR-PRD-0012: Ein Kennungstyp darf pro Produkt nur einmal vorkommen.")


def _type_key(identifier: ProductIdentifier) -> tuple[str, str | None]:
    return identifier.identifier_type.value, identifier.scheme


def _identifier_key(identifier: ProductIdentifier) -> tuple[str, str | None, str]:
    value = re.sub(r"\s+", "", identifier.value).casefold()
    return identifier.identifier_type.value, identifier.scheme, value
