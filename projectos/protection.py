"""Domänenübergreifende Koordination von MCB und RCCB.

Die Regeln bilden ein bewusst kleines ProjectOS-Startprofil ab und ersetzen
keine vollständige Auslegung, Normenprüfung oder Herstellerkoordination.
"""

from __future__ import annotations

from dataclasses import dataclass

from .identifiers import BusinessId, CorrelationId
from .mcb import MCB, validate_mcb
from .rccb import RCCB, validate_rccb
from .results import MessageSeverity, ResultMessage
from .validation import ValidationResult


@dataclass(frozen=True, slots=True)
class ProtectionDevicePair:
    """Unveränderliche Zuordnung eines MCB zu einem vorgeschalteten RCCB."""

    pair_id: BusinessId
    mcb: MCB
    rccb: RCCB

    def __post_init__(self) -> None:
        if not self.pair_id.value.startswith("PAIR-PROT-"):
            raise ValueError("Die Paar-Kennung muss mit PAIR-PROT- beginnen.")


@dataclass(frozen=True, slots=True)
class ProtectionValidationResult:
    """Gesamtergebnis aus Domänen- und Koordinationsvalidierung."""

    pair_id: BusinessId
    mcb_result: ValidationResult
    rccb_result: ValidationResult
    coordination_messages: tuple[ResultMessage, ...]
    correlation_id: CorrelationId | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordination_messages", tuple(self.coordination_messages))

    @property
    def messages(self) -> tuple[ResultMessage, ...]:
        return (
            self.mcb_result.messages
            + self.rccb_result.messages
            + self.coordination_messages
        )

    @property
    def is_valid(self) -> bool:
        return not any(message.is_error for message in self.messages)

    @property
    def errors(self) -> tuple[ResultMessage, ...]:
        return tuple(message for message in self.messages if message.is_error)

    @property
    def warnings(self) -> tuple[ResultMessage, ...]:
        return tuple(
            message
            for message in self.messages
            if message.severity is MessageSeverity.WARNING
        )


def _validate_voltage(pair: ProtectionDevicePair) -> tuple[ResultMessage, ...]:
    if pair.mcb.rated_voltage.volts == pair.rccb.rated_voltage.volts:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-PROT-0001"),
            MessageSeverity.ERROR,
            "MCB und RCCB besitzen unterschiedliche Bemessungsspannungen.",
            {
                "mcb_voltage": pair.mcb.rated_voltage.volts,
                "rccb_voltage": pair.rccb.rated_voltage.volts,
            },
        ),
    )


def _validate_current_coordination(pair: ProtectionDevicePair) -> tuple[ResultMessage, ...]:
    if pair.mcb.nominal_current.amperes <= pair.rccb.rated_current.amperes:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-PROT-0002"),
            MessageSeverity.ERROR,
            "Der MCB-Nennstrom überschreitet den RCCB-Bemessungsstrom.",
            {
                "mcb_current": pair.mcb.nominal_current.amperes,
                "rccb_current": pair.rccb.rated_current.amperes,
            },
        ),
    )


def _validate_pole_coordination(pair: ProtectionDevicePair) -> tuple[ResultMessage, ...]:
    if pair.mcb.pole_count.value <= pair.rccb.pole_count.value:
        return ()
    return (
        ResultMessage(
            BusinessId("ERR-PROT-0003"),
            MessageSeverity.ERROR,
            "Die MCB-Polzahl überschreitet die RCCB-Polzahl.",
            {
                "mcb_poles": pair.mcb.pole_count.value,
                "rccb_poles": pair.rccb.pole_count.value,
            },
        ),
    )


def validate_protection_pair(
    pair: ProtectionDevicePair,
    *,
    correlation_id: CorrelationId | None = None,
) -> ProtectionValidationResult:
    """Validiert beide Geräte und anschließend ihre gemeinsame Koordination."""

    coordination_messages = (
        _validate_voltage(pair)
        + _validate_current_coordination(pair)
        + _validate_pole_coordination(pair)
    )
    return ProtectionValidationResult(
        pair_id=pair.pair_id,
        mcb_result=validate_mcb(pair.mcb),
        rccb_result=validate_rccb(pair.rccb),
        coordination_messages=coordination_messages,
        correlation_id=correlation_id,
    )
