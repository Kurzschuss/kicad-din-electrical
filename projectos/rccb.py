"""Erste fachliche RCCB-Domäne für ProjectOS.

Die enthaltenen Werte bilden ein bewusst kleines ProjectOS-Startprofil ab.
Sie ersetzen keine vollständige Normen-, Hersteller- oder Projektprüfung.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable

from .identifiers import BusinessId, ObjectId
from .repositories import RepositoryEntity
from .results import MessageSeverity, ResultMessage
from .validation import ValidationProfile, Validator


class RCCBType(StrEnum):
    """Im Startprofil unterstützte RCCB-Typen."""

    AC = "AC"
    A = "A"
    F = "F"
    B = "B"


@dataclass(frozen=True, slots=True)
class RatedCurrent:
    """Bemessungsstrom in Ampere."""

    amperes: int

    def __post_init__(self) -> None:
        if not isinstance(self.amperes, int) or isinstance(self.amperes, bool):
            raise TypeError("Der Bemessungsstrom muss als Ganzzahl angegeben werden.")
        if self.amperes <= 0:
            raise ValueError("Der Bemessungsstrom muss größer als 0 A sein.")


@dataclass(frozen=True, slots=True)
class ResidualCurrent:
    """Bemessungsdifferenzstrom in Milliampere."""

    milliamperes: int

    def __post_init__(self) -> None:
        if not isinstance(self.milliamperes, int) or isinstance(self.milliamperes, bool):
            raise TypeError("Der Differenzstrom muss als Ganzzahl angegeben werden.")
        if self.milliamperes <= 0:
            raise ValueError("Der Differenzstrom muss größer als 0 mA sein.")


@dataclass(frozen=True, slots=True)
class RCCBRatedVoltage:
    """Bemessungsspannung in Volt."""

    volts: int

    def __post_init__(self) -> None:
        if not isinstance(self.volts, int) or isinstance(self.volts, bool):
            raise TypeError("Die Bemessungsspannung muss als Ganzzahl angegeben werden.")
        if self.volts <= 0:
            raise ValueError("Die Bemessungsspannung muss größer als 0 V sein.")


@dataclass(frozen=True, slots=True)
class RCCBPoleCount:
    """Polzahl des RCCB."""

    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise TypeError("Die Polzahl muss als Ganzzahl angegeben werden.")
        if self.value not in {2, 4}:
            raise ValueError("Die RCCB-Polzahl muss 2 oder 4 betragen.")


@dataclass(frozen=True, slots=True)
class RCCB(RepositoryEntity):
    """Unveränderliches RCCB-Aggregat des ersten Domain-Slices."""

    object_id: ObjectId
    business_id: BusinessId
    manufacturer: str
    product_name: str
    rated_current: RatedCurrent
    residual_current: ResidualCurrent
    rated_voltage: RCCBRatedVoltage
    pole_count: RCCBPoleCount
    rccb_type: RCCBType

    def __post_init__(self) -> None:
        manufacturer = self.manufacturer.strip()
        product_name = self.product_name.strip()
        if not manufacturer:
            raise ValueError("Der Hersteller darf nicht leer sein.")
        if not product_name:
            raise ValueError("Die Produktbezeichnung darf nicht leer sein.")
        if not self.business_id.value.startswith("RCCB-"):
            raise ValueError("Die fachliche Kennung eines RCCB muss mit RCCB- beginnen.")
        object.__setattr__(self, "manufacturer", manufacturer)
        object.__setattr__(self, "product_name", product_name)


@dataclass(frozen=True, slots=True)
class _RCCBRule:
    rule_id: BusinessId
    check: Callable[[RCCB], tuple[ResultMessage, ...]]

    def validate(self, value: RCCB) -> tuple[ResultMessage, ...]:
        return self.check(value)


_SUPPORTED_RATED_CURRENTS = frozenset({16, 25, 40, 63, 80, 100})
_SUPPORTED_RESIDUAL_CURRENTS = frozenset({10, 30, 100, 300, 500})
_SUPPORTED_VOLTAGES = frozenset({230, 400})


def _validate_rated_current(rccb: RCCB) -> tuple[ResultMessage, ...]:
    if rccb.rated_current.amperes in _SUPPORTED_RATED_CURRENTS:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-RCCB-0001"),
            MessageSeverity.ERROR,
            "Der Bemessungsstrom ist im ProjectOS-RCCB-Startprofil nicht freigegeben.",
            {"value": rccb.rated_current.amperes},
        ),
    )


def _validate_residual_current(rccb: RCCB) -> tuple[ResultMessage, ...]:
    if rccb.residual_current.milliamperes in _SUPPORTED_RESIDUAL_CURRENTS:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-RCCB-0002"),
            MessageSeverity.ERROR,
            "Der Differenzstrom ist im ProjectOS-RCCB-Startprofil nicht freigegeben.",
            {"value": rccb.residual_current.milliamperes},
        ),
    )


def _validate_voltage_and_poles(rccb: RCCB) -> tuple[ResultMessage, ...]:
    if rccb.rated_voltage.volts not in _SUPPORTED_VOLTAGES:
        return (
            ResultMessage(
                BusinessId("ERR-RCCB-0003"),
                MessageSeverity.ERROR,
                "Die Bemessungsspannung ist im ProjectOS-RCCB-Startprofil nicht freigegeben.",
                {"value": rccb.rated_voltage.volts},
            ),
        )
    if rccb.rated_voltage.volts == 400 and rccb.pole_count.value != 4:
        return (
            ResultMessage(
                BusinessId("ERR-RCCB-0004"),
                MessageSeverity.ERROR,
                "400-V-RCCB müssen im Startprofil vierpolig modelliert werden.",
                {"poles": rccb.pole_count.value},
            ),
        )
    return ()


def _warn_type_ac(rccb: RCCB) -> tuple[ResultMessage, ...]:
    if rccb.rccb_type is RCCBType.AC:
        return (
            ResultMessage(
                BusinessId("WARN-RCCB-0001"),
                MessageSeverity.WARNING,
                "RCCB Typ AC benötigt eine projektspezifische Eignungsprüfung.",
            ),
        )
    return ()


def create_rccb_validation_profile() -> ValidationProfile[RCCB]:
    """Erzeugt das versionierte Startprofil der RCCB-Domäne."""

    return ValidationProfile(
        profile_id=BusinessId("VAL-RCCB-DEFAULT-0001"),
        rules=(
            _RCCBRule(BusinessId("REQ-RCCB-0001"), _validate_rated_current),
            _RCCBRule(BusinessId("REQ-RCCB-0002"), _validate_residual_current),
            _RCCBRule(BusinessId("REQ-RCCB-0003"), _validate_voltage_and_poles),
            _RCCBRule(BusinessId("REQ-RCCB-0004"), _warn_type_ac),
        ),
    )


def validate_rccb(rccb: RCCB):
    """Validiert einen RCCB gegen das ProjectOS-Startprofil."""

    return Validator[RCCB]().validate(rccb, create_rccb_validation_profile())
