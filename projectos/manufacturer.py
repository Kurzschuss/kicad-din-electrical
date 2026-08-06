"""Hersteller-, Produktserien- und Herstellerreferenzmodell für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from urllib.parse import urlparse

from .identifiers import BusinessId, ObjectId


class ManufacturerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True, slots=True)
class Manufacturer:
    object_id: ObjectId
    manufacturer_id: BusinessId
    name: str
    short_name: str | None = None
    country_code: str | None = None
    website: str | None = None
    support_url: str | None = None
    status: ManufacturerStatus = ManufacturerStatus.ACTIVE
    revision: int = 0

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("ERR-MAN-0001: Ein Hersteller benötigt einen Namen.")
        short_name = self.short_name.strip() if self.short_name else None
        country_code = self.country_code.strip().upper() if self.country_code else None
        if country_code is not None and (len(country_code) != 2 or not country_code.isalpha()):
            raise ValueError("Der Ländercode muss ISO-3166-Alpha-2 entsprechen.")
        _validate_url(self.website, "website")
        _validate_url(self.support_url, "support_url")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "short_name", short_name)
        object.__setattr__(self, "country_code", country_code)

    def rename(self, name: str, *, short_name: str | None = None) -> "Manufacturer":
        return replace(self, name=name, short_name=short_name, revision=self.revision + 1)

    def deactivate(self) -> "Manufacturer":
        if self.status is ManufacturerStatus.INACTIVE:
            return self
        return replace(self, status=ManufacturerStatus.INACTIVE, revision=self.revision + 1)

    def activate(self) -> "Manufacturer":
        if self.status is ManufacturerStatus.ACTIVE:
            return self
        return replace(self, status=ManufacturerStatus.ACTIVE, revision=self.revision + 1)


@dataclass(frozen=True, slots=True)
class ProductSeries:
    object_id: ObjectId
    series_id: BusinessId
    manufacturer_id: BusinessId
    name: str
    description: str = ""
    active: bool = True
    revision: int = 0

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("Eine Produktserie benötigt einen Namen.")
        description = self.description.strip()
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)

    def rename(self, name: str) -> "ProductSeries":
        return replace(self, name=name, revision=self.revision + 1)

    def deactivate(self) -> "ProductSeries":
        if not self.active:
            return self
        return replace(self, active=False, revision=self.revision + 1)


@dataclass(frozen=True, slots=True)
class ManufacturerReference:
    object_id: ObjectId
    reference_id: BusinessId
    catalog_device_id: BusinessId
    manufacturer_id: BusinessId
    series_id: BusinessId | None = None
    product_name: str | None = None
    revision: int = 0

    def __post_init__(self) -> None:
        product_name = self.product_name.strip() if self.product_name else None
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "product_name", product_name)

    @classmethod
    def create(
        cls,
        *,
        object_id: ObjectId,
        reference_id: BusinessId,
        catalog_device_id: BusinessId,
        manufacturer: Manufacturer,
        series: ProductSeries | None = None,
        product_name: str | None = None,
    ) -> "ManufacturerReference":
        if series is not None and series.manufacturer_id != manufacturer.manufacturer_id:
            raise ValueError("ERR-MAN-0002: Die Produktserie gehört zu einem anderen Hersteller.")
        if manufacturer.status is not ManufacturerStatus.ACTIVE:
            raise ValueError("ERR-MAN-0003: Eine Herstellerreferenz benötigt einen aktiven Hersteller.")
        if series is not None and not series.active:
            raise ValueError("ERR-MAN-0003: Eine Herstellerreferenz benötigt eine aktive Produktserie.")
        return cls(
            object_id=object_id,
            reference_id=reference_id,
            catalog_device_id=catalog_device_id,
            manufacturer_id=manufacturer.manufacturer_id,
            series_id=series.series_id if series else None,
            product_name=product_name,
        )


def ensure_unique_series_name(
    existing: tuple[ProductSeries, ...],
    candidate: ProductSeries,
) -> None:
    normalized = candidate.name.casefold()
    for series in existing:
        if (
            series.manufacturer_id == candidate.manufacturer_id
            and series.series_id != candidate.series_id
            and series.name.casefold() == normalized
        ):
            raise ValueError(
                "ERR-MAN-0004: Der Serienname ist für diesen Hersteller bereits vorhanden."
            )


def _validate_url(value: str | None, field_name: str) -> None:
    if value is None:
        return
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{field_name} muss eine vollständige HTTP- oder HTTPS-URL sein.")
