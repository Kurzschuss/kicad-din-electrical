"""Normen-, Regelwerks- und Konformitätsreferenzmodell für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum

from .identifiers import BusinessId, ObjectId


class StandardBody(StrEnum):
    IEC = "IEC"
    DIN = "DIN"
    VDE = "VDE"
    EN = "EN"
    ISO = "ISO"
    OTHER = "OTHER"


class StandardStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    WITHDRAWN = "WITHDRAWN"


class ConformityTargetType(StrEnum):
    CATALOG_DEVICE = "CATALOG_DEVICE"
    MANUFACTURER_PRODUCT = "MANUFACTURER_PRODUCT"


class ConformityStatus(StrEnum):
    CLAIMED = "CLAIMED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True, slots=True)
class StandardReference:
    object_id: ObjectId
    standard_id: BusinessId
    body: StandardBody
    designation: str
    title: str
    edition: str
    publication_date: date | None = None
    status: StandardStatus = StandardStatus.DRAFT
    revision: int = 0

    def __post_init__(self) -> None:
        designation = self.designation.strip()
        title = self.title.strip()
        edition = self.edition.strip()
        if not designation:
            raise ValueError("ERR-STD-0001: Eine Norm benötigt eine Bezeichnung.")
        if not title:
            raise ValueError("ERR-STD-0002: Eine Norm benötigt einen Titel.")
        if not edition:
            raise ValueError("ERR-STD-0003: Eine Norm benötigt eine Ausgabe.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "designation", designation)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "edition", edition)

    def activate(self) -> "StandardReference":
        if self.status is StandardStatus.WITHDRAWN:
            raise ValueError("ERR-STD-0004: Eine zurückgezogene Norm darf nicht reaktiviert werden.")
        if self.status is StandardStatus.ACTIVE:
            return self
        return replace(self, status=StandardStatus.ACTIVE, revision=self.revision + 1)

    def withdraw(self) -> "StandardReference":
        if self.status is StandardStatus.WITHDRAWN:
            return self
        return replace(self, status=StandardStatus.WITHDRAWN, revision=self.revision + 1)


@dataclass(frozen=True, slots=True)
class ConformityReference:
    object_id: ObjectId
    conformity_id: BusinessId
    target_type: ConformityTargetType
    target_id: BusinessId
    standard_id: BusinessId
    status: ConformityStatus
    evidence_reference: str | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    revision: int = 0

    def __post_init__(self) -> None:
        evidence = self.evidence_reference.strip() if self.evidence_reference else None
        if self.status is ConformityStatus.VERIFIED and not evidence:
            raise ValueError("ERR-STD-0005: Eine verifizierte Konformität benötigt einen Nachweis.")
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("ERR-STD-0006: Das Gültigkeitsende liegt vor dem Beginn.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "evidence_reference", evidence)

    @classmethod
    def create(
        cls,
        *,
        object_id: ObjectId,
        conformity_id: BusinessId,
        target_type: ConformityTargetType,
        target_id: BusinessId,
        standard: StandardReference,
        status: ConformityStatus = ConformityStatus.CLAIMED,
        evidence_reference: str | None = None,
        valid_from: date | None = None,
        valid_until: date | None = None,
    ) -> "ConformityReference":
        if standard.status is not StandardStatus.ACTIVE:
            raise ValueError("ERR-STD-0007: Konformität darf nur auf eine aktive Norm verweisen.")
        return cls(
            object_id=object_id,
            conformity_id=conformity_id,
            target_type=target_type,
            target_id=target_id,
            standard_id=standard.standard_id,
            status=status,
            evidence_reference=evidence_reference,
            valid_from=valid_from,
            valid_until=valid_until,
        )


def ensure_unique_standard_edition(
    existing: tuple[StandardReference, ...],
    candidate: StandardReference,
) -> None:
    designation = candidate.designation.casefold()
    edition = candidate.edition.casefold()
    for standard in existing:
        if (
            standard.standard_id != candidate.standard_id
            and standard.body is candidate.body
            and standard.designation.casefold() == designation
            and standard.edition.casefold() == edition
        ):
            raise ValueError("ERR-STD-0008: Diese Normausgabe ist bereits vorhanden.")
