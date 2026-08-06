"""Fachliche Anschlüsse und ihre Zuordnung zu KiCad-Symbolpins.

KiCad-Verträge sind der verbindliche Regelfall. Abweichungen sind nur als ausdrücklich
begründete Ausnahme zulässig.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from .identifiers import BusinessId, ObjectId
from .kicad_assets import (
    KiCadAssetReference,
    KiCadAssetStatus,
    KiCadAssetTargetType,
    KiCadAssetType,
)


class TerminalFunction(StrEnum):
    POWER = "POWER"
    CONTROL = "CONTROL"
    SIGNAL = "SIGNAL"
    NEUTRAL = "NEUTRAL"
    PROTECTIVE_EARTH = "PROTECTIVE_EARTH"
    AUXILIARY = "AUXILIARY"
    OTHER = "OTHER"


class KiCadPinElectricalType(StrEnum):
    """Elektrische Pin-Typen entsprechend dem KiCad-Symbolmodell."""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    TRI_STATE = "TRI_STATE"
    PASSIVE = "PASSIVE"
    FREE = "FREE"
    UNSPECIFIED = "UNSPECIFIED"
    POWER_INPUT = "POWER_INPUT"
    POWER_OUTPUT = "POWER_OUTPUT"
    OPEN_COLLECTOR = "OPEN_COLLECTOR"
    OPEN_EMITTER = "OPEN_EMITTER"
    NO_CONNECT = "NO_CONNECT"


class KiCadStandardConformance(StrEnum):
    STANDARD = "STANDARD"
    EXCEPTION = "EXCEPTION"


@dataclass(frozen=True, slots=True)
class DeviceTerminal:
    """Fachlicher Anschluss eines Kataloggeräts oder Herstellerprodukts."""

    object_id: ObjectId
    terminal_id: BusinessId
    target_type: KiCadAssetTargetType
    target_id: BusinessId
    designation: str
    function: TerminalFunction
    required: bool = True
    description: str = ""
    revision: int = 0

    def __post_init__(self) -> None:
        designation = self.designation.strip()
        description = self.description.strip()
        if not designation:
            raise ValueError("ERR-KICAD-0008: Ein Anschluss benötigt eine Bezeichnung.")
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "designation", designation)
        object.__setattr__(self, "description", description)

    def rename(self, designation: str, *, description: str | None = None) -> "DeviceTerminal":
        return replace(
            self,
            designation=designation,
            description=self.description if description is None else description,
            revision=self.revision + 1,
        )


@dataclass(frozen=True, slots=True)
class KiCadSymbolPin:
    """Pinidentität gemäß KiCad-Symbolmodell."""

    number: str
    name: str
    electrical_type: KiCadPinElectricalType = KiCadPinElectricalType.PASSIVE
    unit: int = 1

    def __post_init__(self) -> None:
        number = self.number.strip()
        name = self.name.strip()
        if not number:
            raise ValueError("ERR-KICAD-0009: Eine KiCad-Pinnummer darf nicht leer sein.")
        if self.unit < 1:
            raise ValueError("ERR-KICAD-0010: Die KiCad-Symboleinheit muss mindestens 1 sein.")
        object.__setattr__(self, "number", number)
        object.__setattr__(self, "name", name)


@dataclass(frozen=True, slots=True)
class TerminalPinAssignment:
    """Eindeutige Zuordnung eines fachlichen Anschlusses zu einem Symbolpin."""

    object_id: ObjectId
    assignment_id: BusinessId
    terminal_id: BusinessId
    symbol_asset_id: BusinessId
    pin: KiCadSymbolPin
    conformance: KiCadStandardConformance = KiCadStandardConformance.STANDARD
    exception_reason: str | None = None
    revision: int = 0

    def __post_init__(self) -> None:
        reason = self.exception_reason.strip() if self.exception_reason else None
        if self.conformance is KiCadStandardConformance.EXCEPTION and not reason:
            raise ValueError(
                "ERR-KICAD-0016: Eine Abweichung vom KiCad-Standard benötigt eine Begründung."
            )
        if self.conformance is KiCadStandardConformance.STANDARD and reason is not None:
            raise ValueError(
                "ERR-KICAD-0017: Ein standardkonformer Eintrag darf keinen Ausnahmegrund enthalten."
            )
        if self.revision < 0:
            raise ValueError("Die Revision darf nicht negativ sein.")
        object.__setattr__(self, "exception_reason", reason)

    @classmethod
    def create(
        cls,
        *,
        object_id: ObjectId,
        assignment_id: BusinessId,
        terminal: DeviceTerminal,
        symbol_asset: KiCadAssetReference,
        pin: KiCadSymbolPin,
        conformance: KiCadStandardConformance = KiCadStandardConformance.STANDARD,
        exception_reason: str | None = None,
    ) -> "TerminalPinAssignment":
        if symbol_asset.asset_type is not KiCadAssetType.SYMBOL:
            raise ValueError("ERR-KICAD-0011: Anschlusszuordnungen benötigen ein KiCad-Symbol.")
        if symbol_asset.status is not KiCadAssetStatus.ACTIVE:
            raise ValueError("ERR-KICAD-0012: Anschlusszuordnungen benötigen ein aktives KiCad-Symbol.")
        if (
            symbol_asset.target_type is not terminal.target_type
            or symbol_asset.target_id != terminal.target_id
        ):
            raise ValueError("ERR-KICAD-0013: Anschluss und Symbol gehören nicht zum selben Ziel.")
        return cls(
            object_id=object_id,
            assignment_id=assignment_id,
            terminal_id=terminal.terminal_id,
            symbol_asset_id=symbol_asset.asset_id,
            pin=pin,
            conformance=conformance,
            exception_reason=exception_reason,
        )

    def change_pin(
        self,
        pin: KiCadSymbolPin,
        *,
        conformance: KiCadStandardConformance = KiCadStandardConformance.STANDARD,
        exception_reason: str | None = None,
    ) -> "TerminalPinAssignment":
        return replace(
            self,
            pin=pin,
            conformance=conformance,
            exception_reason=exception_reason,
            revision=self.revision + 1,
        )


def ensure_unique_terminal_pin_assignment(
    existing: tuple[TerminalPinAssignment, ...],
    candidate: TerminalPinAssignment,
) -> None:
    for assignment in existing:
        if assignment.assignment_id == candidate.assignment_id:
            continue
        if (
            assignment.symbol_asset_id == candidate.symbol_asset_id
            and assignment.terminal_id == candidate.terminal_id
        ):
            raise ValueError("ERR-KICAD-0014: Der Anschluss ist diesem Symbol bereits zugeordnet.")
        if (
            assignment.symbol_asset_id == candidate.symbol_asset_id
            and assignment.pin.unit == candidate.pin.unit
            and assignment.pin.number.casefold() == candidate.pin.number.casefold()
        ):
            raise ValueError("ERR-KICAD-0015: Der Symbolpin ist bereits einem Anschluss zugeordnet.")


def validate_required_terminal_assignments(
    terminals: tuple[DeviceTerminal, ...],
    assignments: tuple[TerminalPinAssignment, ...],
    symbol_asset: KiCadAssetReference,
) -> tuple[BusinessId, ...]:
    """Liefert erforderliche, noch nicht zugeordnete Anschlüsse."""
    if symbol_asset.asset_type is not KiCadAssetType.SYMBOL:
        raise ValueError("ERR-KICAD-0011: Die Vollständigkeitsprüfung benötigt ein KiCad-Symbol.")

    assigned = {
        assignment.terminal_id
        for assignment in assignments
        if assignment.symbol_asset_id == symbol_asset.asset_id
    }
    return tuple(
        terminal.terminal_id
        for terminal in terminals
        if terminal.required
        and terminal.target_type is symbol_asset.target_type
        and terminal.target_id == symbol_asset.target_id
        and terminal.terminal_id not in assigned
    )
