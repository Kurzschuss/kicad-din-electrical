"""Erste fachliche MCB-Domäne für ProjectOS.

Die hier enthaltenen Grenzwerte bilden ein bewusst kleines ProjectOS-Startprofil ab.
Sie ersetzen keine vollständige Normen- oder Herstellerprüfung.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .identifiers import BusinessId, ObjectId
from .repositories import RepositoryEntity
from .results import MessageSeverity, ResultMessage
from .validation import ValidationProfile, ValidationResult, Validator


class TripCharacteristic(StrEnum):
    """Unterstützte Auslösecharakteristiken des Startprofils."""

    B = "B"
    C = "C"
    D = "D"


@dataclass(frozen=True, slots=True)
class NominalCurrent:
    amperes: int

    def __post_init__(self) -> None:
        if not isinstance(self.amperes, int) or isinstance(self.amperes, bool):
            raise TypeError("Der Nennstrom muss als Ganzzahl angegeben werden.")
        if self.amperes <= 0:
            raise ValueError("Der Nennstrom muss größer als 0 A sein.")


@dataclass(frozen=True, slots=True)
class RatedVoltage:
    volts: int

    def __post_init__(self) -> None:
        if not isinstance(self.volts, int) or isinstance(self.volts, bool):
            raise TypeError("Die Bemessungsspannung muss als Ganzzahl angegeben werden.")
        if self.volts <= 0:
            raise ValueError("Die Bemessungsspannung muss größer als 0 V sein.")


@dataclass(frozen=True, slots=True)
class BreakingCapacity:
    amperes: int

    def __post_init__(self) -> None:
        if not isinstance(self.amperes, int) or isinstance(self.amperes, bool):
            raise TypeError("Das Schaltvermögen muss als Ganzzahl angegeben werden.")
        if self.amperes <= 0:
            raise ValueError("Das Schaltvermögen muss größer als 0 A sein.")


@dataclass(frozen=True, slots=True)
class PoleCount:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise TypeError("Die Polzahl muss als Ganzzahl angegeben werden.")
        if self.value not in {1, 2, 3, 4}:
            raise ValueError("Die Polzahl muss 1, 2, 3 oder 4 betragen.")


@dataclass(frozen=True, slots=True)
class MCB(RepositoryEntity):
    """Unveränderliches MCB-Aggregat des ersten Domain-Slices."""

    object_id: ObjectId
    business_id: BusinessId
    manufacturer: str
    product_name: str
    nominal_current: NominalCurrent
    rated_voltage: RatedVoltage
    trip_characteristic: TripCharacteristic
    pole_count: PoleCount
    breaking_capacity: BreakingCapacity

    def __post_init__(self) -> None:
        manufacturer = self.manufacturer.strip()
        product_name = self.product_name.strip()
        if not manufacturer:
            raise ValueError("Der Hersteller darf nicht leer sein.")
        if not product_name:
            raise ValueError("Die Produktbezeichnung darf nicht leer sein.")
        if not self.business_id.value.startswith("MCB-"):
            raise ValueError("Die fachliche Kennung eines MCB muss mit MCB- beginnen.")
        object.__setattr__(self, "manufacturer", manufacturer)
        object.__setattr__(self, "product_name", product_name)


RuleFunction = Callable[[MCB], tuple[ResultMessage, ...]]


@dataclass(frozen=True, slots=True)
class MCBValidationRule:
    """Kleiner Adapter für den generischen ValidationRule-Vertrag."""

    rule_id: BusinessId
    check: RuleFunction

    def validate(self, value: MCB) -> tuple[ResultMessage, ...]:
        return self.check(value)


_SUPPORTED_NOMINAL_CURRENTS = frozenset({2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63})
_SUPPORTED_VOLTAGES = frozenset({230, 400})
_SUPPORTED_BREAKING_CAPACITIES = frozenset({4500, 6000, 10000})


def _validate_nominal_current(mcb: MCB) -> tuple[ResultMessage, ...]:
    if mcb.nominal_current.amperes in _SUPPORTED_NOMINAL_CURRENTS:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-MCB-0001"),
            MessageSeverity.ERROR,
            "Der Nennstrom ist im ProjectOS-MCB-Startprofil nicht freigegeben.",
            {"value": mcb.nominal_current.amperes},
        ),
    )


def _validate_voltage(mcb: MCB) -> tuple[ResultMessage, ...]:
    if mcb.rated_voltage.volts in _SUPPORTED_VOLTAGES:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-MCB-0002"),
            MessageSeverity.ERROR,
            "Die Bemessungsspannung ist im ProjectOS-MCB-Startprofil nicht freigegeben.",
            {"value": mcb.rated_voltage.volts},
        ),
    )


def _validate_breaking_capacity(mcb: MCB) -> tuple[ResultMessage, ...]:
    if mcb.breaking_capacity.amperes in _SUPPORTED_BREAKING_CAPACITIES:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-MCB-0003"),
            MessageSeverity.ERROR,
            "Das Schaltvermögen ist im ProjectOS-MCB-Startprofil nicht freigegeben.",
            {"value": mcb.breaking_capacity.amperes},
        ),
    )


def _warn_high_current_single_pole(mcb: MCB) -> tuple[ResultMessage, ...]:
    if mcb.pole_count.value == 1 and mcb.nominal_current.amperes > 40:
        return (
            ResultMessage(
                BusinessId("WARN-MCB-0001"),
                MessageSeverity.WARNING,
                "Ein einpoliger MCB über 40 A benötigt eine projektspezifische Prüfung.",
                {"nominal_current": mcb.nominal_current.amperes},
            ),
        )
    return ()


def create_mcb_validation_profile() -> ValidationProfile[MCB]:
    """Erzeugt das versionierte Startprofil der MCB-Domäne."""

    return ValidationProfile(
        profile_id=BusinessId("VAL-MCB-DEFAULT-0001"),
        rules=(
            MCBValidationRule(BusinessId("REQ-MCB-0001"), _validate_nominal_current),
            MCBValidationRule(BusinessId("REQ-MCB-0002"), _validate_voltage),
            MCBValidationRule(BusinessId("REQ-MCB-0003"), _validate_breaking_capacity),
            MCBValidationRule(BusinessId("REQ-MCB-0004"), _warn_high_current_single_pole),
        ),
    )


def validate_mcb(mcb: MCB) -> ValidationResult:
    """Validiert ein MCB gegen das ProjectOS-Startprofil."""

    return Validator[MCB]().validate(mcb, create_mcb_validation_profile())
