"""Deterministisches Validierungsframework für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Protocol, TypeVar

from .identifiers import BusinessId, CorrelationId
from .results import MessageSeverity, ResultMessage

T = TypeVar("T")


class ValidationRule(Protocol[T]):
    """Vertrag einer einzelnen, zustandslosen Validierungsregel."""

    rule_id: BusinessId

    def validate(self, value: T) -> tuple[ResultMessage, ...]:
        """Prüft einen Wert und liefert strukturierte Meldungen."""
        ...


@dataclass(frozen=True, slots=True)
class ValidationProfile(Generic[T]):
    """Geordnete, unveränderliche Zusammenstellung von Regeln."""

    profile_id: BusinessId
    rules: tuple[ValidationRule[T], ...]
    stop_on_critical: bool = True

    def __post_init__(self) -> None:
        rules = tuple(self.rules)
        if not rules:
            raise ValueError("Ein Validierungsprofil benötigt mindestens eine Regel.")
        rule_ids = [rule.rule_id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("Ein Validierungsprofil darf keine Regel doppelt enthalten.")
        object.__setattr__(self, "rules", rules)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Vollständiges Ergebnis eines reproduzierbaren Validierungslaufs."""

    profile_id: BusinessId
    messages: tuple[ResultMessage, ...]
    correlation_id: CorrelationId | None = None
    executed_rule_ids: tuple[BusinessId, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "messages", tuple(self.messages))
        object.__setattr__(self, "executed_rule_ids", tuple(self.executed_rule_ids))

    @property
    def is_valid(self) -> bool:
        return not any(message.is_error for message in self.messages)

    @property
    def errors(self) -> tuple[ResultMessage, ...]:
        return tuple(message for message in self.messages if message.is_error)

    @property
    def warnings(self) -> tuple[ResultMessage, ...]:
        return tuple(
            message for message in self.messages if message.severity is MessageSeverity.WARNING
        )


class Validator(Generic[T]):
    """Führt ein Profil strikt in der definierten Regelreihenfolge aus."""

    def validate(
        self,
        value: T,
        profile: ValidationProfile[T],
        *,
        correlation_id: CorrelationId | None = None,
    ) -> ValidationResult:
        messages: list[ResultMessage] = []
        executed_rule_ids: list[BusinessId] = []

        for rule in profile.rules:
            rule_messages = tuple(rule.validate(value))
            self._validate_messages(rule_messages)
            executed_rule_ids.append(rule.rule_id)
            messages.extend(rule_messages)

            if profile.stop_on_critical and any(
                message.severity is MessageSeverity.CRITICAL for message in rule_messages
            ):
                break

        return ValidationResult(
            profile_id=profile.profile_id,
            messages=tuple(messages),
            correlation_id=correlation_id,
            executed_rule_ids=tuple(executed_rule_ids),
        )

    @staticmethod
    def _validate_messages(messages: Iterable[ResultMessage]) -> None:
        for message in messages:
            if not isinstance(message, ResultMessage):
                raise TypeError("Validierungsregeln dürfen nur ResultMessage-Objekte liefern.")
