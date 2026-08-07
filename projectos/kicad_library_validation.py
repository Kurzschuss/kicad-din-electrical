"""Deterministische Prüfung von KiCad-Bibliotheksreferenzen."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .identifiers import BusinessId
from .kicad_assets import KiCadAssetReference, KiCadAssetType
from .kicad_connections import TerminalPinAssignment


class KiCadAssetRequirement(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class KiCadValidationSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True, slots=True)
class KiCadLibraryItemSnapshot:
    asset_type: KiCadAssetType
    qualified_name: str
    pin_numbers: tuple[str, ...] = ()
    checksum_sha256: str | None = None

    def __post_init__(self) -> None:
        name = self.qualified_name.strip()
        if not name or ":" not in name:
            raise ValueError("ERR-KICAD-0018: Eine Bibliotheksreferenz muss qualifiziert sein.")
        pins = tuple(dict.fromkeys(pin.strip() for pin in self.pin_numbers if pin.strip()))
        checksum = self.checksum_sha256.strip().lower() if self.checksum_sha256 else None
        if checksum is not None and (len(checksum) != 64 or any(ch not in "0123456789abcdef" for ch in checksum)):
            raise ValueError("ERR-KICAD-0004: Die SHA-256-Prüfsumme ist ungültig.")
        object.__setattr__(self, "qualified_name", name)
        object.__setattr__(self, "pin_numbers", pins)
        object.__setattr__(self, "checksum_sha256", checksum)


@dataclass(frozen=True, slots=True)
class KiCadTargetRequirements:
    symbol: KiCadAssetRequirement = KiCadAssetRequirement.REQUIRED
    footprint: KiCadAssetRequirement = KiCadAssetRequirement.OPTIONAL
    model_3d: KiCadAssetRequirement = KiCadAssetRequirement.OPTIONAL

    def for_type(self, asset_type: KiCadAssetType) -> KiCadAssetRequirement:
        if asset_type is KiCadAssetType.SYMBOL:
            return self.symbol
        if asset_type is KiCadAssetType.FOOTPRINT:
            return self.footprint
        return self.model_3d


@dataclass(frozen=True, slots=True)
class KiCadValidationFinding:
    code: str
    severity: KiCadValidationSeverity
    message: str
    asset_id: BusinessId | None = None


@dataclass(frozen=True, slots=True)
class KiCadLibraryValidationResult:
    findings: tuple[KiCadValidationFinding, ...]

    @property
    def valid(self) -> bool:
        return not any(item.severity is KiCadValidationSeverity.ERROR for item in self.findings)


class KiCadLibraryValidator:
    def __init__(self, snapshot: tuple[KiCadLibraryItemSnapshot, ...]) -> None:
        self._snapshot = {
            (item.asset_type, item.qualified_name.casefold()): item
            for item in snapshot
        }

    def validate(
        self,
        *,
        assets: tuple[KiCadAssetReference, ...],
        assignments: tuple[TerminalPinAssignment, ...] = (),
        requirements: KiCadTargetRequirements | None = None,
    ) -> KiCadLibraryValidationResult:
        requirements = requirements or KiCadTargetRequirements()
        findings: list[KiCadValidationFinding] = []
        present_types = {asset.asset_type for asset in assets}

        for asset_type in KiCadAssetType:
            requirement = requirements.for_type(asset_type)
            if requirement is KiCadAssetRequirement.REQUIRED and asset_type not in present_types:
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0019",
                    KiCadValidationSeverity.ERROR,
                    f"Erforderliches KiCad-Artefakt fehlt: {asset_type.value}.",
                ))
            elif requirement is KiCadAssetRequirement.NOT_APPLICABLE and asset_type in present_types:
                findings.append(KiCadValidationFinding(
                    "WARN-KICAD-0001",
                    KiCadValidationSeverity.WARNING,
                    f"Artefakt vorhanden, obwohl nicht anwendbar: {asset_type.value}.",
                ))

        symbols: dict[BusinessId, KiCadLibraryItemSnapshot] = {}
        for asset in assets:
            item = self._snapshot.get((asset.asset_type, asset.reference.qualified_name.casefold()))
            if item is None:
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0020",
                    KiCadValidationSeverity.ERROR,
                    f"Bibliothekseintrag nicht gefunden: {asset.reference.qualified_name}.",
                    asset.asset_id,
                ))
                continue
            if asset.checksum_sha256 and item.checksum_sha256 != asset.checksum_sha256:
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0021",
                    KiCadValidationSeverity.ERROR,
                    f"Prüfsumme stimmt nicht überein: {asset.reference.qualified_name}.",
                    asset.asset_id,
                ))
            if asset.asset_type is KiCadAssetType.SYMBOL:
                symbols[asset.asset_id] = item

        for assignment in assignments:
            symbol = symbols.get(assignment.symbol_asset_id)
            if symbol and assignment.pin.number not in symbol.pin_numbers:
                findings.append(KiCadValidationFinding(
                    "ERR-KICAD-0022",
                    KiCadValidationSeverity.ERROR,
                    f"Symbolpin {assignment.pin.number} fehlt in {symbol.qualified_name}.",
                    assignment.symbol_asset_id,
                ))

        return KiCadLibraryValidationResult(tuple(findings))
