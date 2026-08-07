"""KiCad-Symbol-, Footprint- und 3D-Modellreferenzen für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import PurePosixPath

from .identifiers import BusinessId, ObjectId


class KiCadAssetType(StrEnum):
    SYMBOL = "SYMBOL"
    FOOTPRINT = "FOOTPRINT"
    MODEL_3D = "MODEL_3D"


class KiCadAssetTargetType(StrEnum):
    CATALOG_DEVICE = "CATALOG_DEVICE"
    MANUFACTURER_PRODUCT = "MANUFACTURER_PRODUCT"


class KiCadAssetStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


@dataclass(frozen=True, slots=True)
class KiCadLibraryReference:
    library: str
    item_name: str
    relative_path: str | None = None

    def __post_init__(self) -> None:
        library = self.library.strip()
        item_name = self.item_name.strip()
        if not library:
            raise ValueError("ERR-KICAD-0001: Der Bibliotheksname darf nicht leer sein.")
        if not item_name:
            raise ValueError("ERR-KICAD-0002: Der Artefaktname darf nicht leer sein.")
        relative_path = self.relative_path.strip().replace("\\", "/") if self.relative_path else None
        if relative_path is not None:
            path = PurePosixPath(relative_path)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("ERR-KICAD-0003: Der Bibliothekspfad muss relativ und sicher sein.")
        object.__setattr__(self, "library", library)
        object.__setattr__(self, "item_name", item_name)
        object.__setattr__(self, "relative_path", relative_path)

    @property
    def qualified_name(self) -> str:
        return f"{self.library}:{self.item_name}"


@dataclass(frozen=True, slots=True)
class KiCadAssetReference:
    object_id: ObjectId
    asset_id: BusinessId
    asset_type: KiCadAssetType
    target_type: KiCadAssetTargetType
    target_id: BusinessId
    reference: KiCadLibraryReference
    status: KiCadAssetStatus = KiCadAssetStatus.DRAFT
    checksum_sha256: str | None = None
    revision: int = 0

    def __post_init__(self) -> None:
        checksum = self.checksum_sha256.strip().lower() if self.checksum_sha256 else None
        if checksum is not None and (len(checksum) != 64 or any(ch not in "0123456789abcdef" for ch in checksum)):
            raise ValueError("ERR-KICAD-0004: Die SHA-256-Prüfsumme ist ungültig.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "checksum_sha256", checksum)

    def activate(self) -> "KiCadAssetReference":
        if self.status is KiCadAssetStatus.RETIRED:
            raise ValueError("ERR-KICAD-0005: Ein ausgemustertes KiCad-Artefakt darf nicht reaktiviert werden.")
        if self.status is KiCadAssetStatus.ACTIVE:
            return self
        return replace(self, status=KiCadAssetStatus.ACTIVE, revision=self.revision + 1)

    def retire(self) -> "KiCadAssetReference":
        if self.status is KiCadAssetStatus.RETIRED:
            return self
        return replace(self, status=KiCadAssetStatus.RETIRED, revision=self.revision + 1)

    def update_reference(
        self,
        reference: KiCadLibraryReference,
        *,
        checksum_sha256: str | None = None,
    ) -> "KiCadAssetReference":
        if self.status is KiCadAssetStatus.RETIRED:
            raise ValueError("ERR-KICAD-0006: Ein ausgemustertes KiCad-Artefakt darf nicht geändert werden.")
        return replace(
            self,
            reference=reference,
            checksum_sha256=checksum_sha256,
            revision=self.revision + 1,
        )


def ensure_unique_kicad_asset(
    existing: tuple[KiCadAssetReference, ...],
    candidate: KiCadAssetReference,
) -> None:
    for asset in existing:
        if (
            asset.asset_id != candidate.asset_id
            and asset.target_type is candidate.target_type
            and asset.target_id == candidate.target_id
            and asset.asset_type is candidate.asset_type
            and asset.reference.qualified_name.casefold() == candidate.reference.qualified_name.casefold()
        ):
            raise ValueError("ERR-KICAD-0007: Diese KiCad-Referenz ist dem Ziel bereits zugeordnet.")
