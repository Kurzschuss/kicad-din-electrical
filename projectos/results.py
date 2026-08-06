"""Strukturierte Ergebnisobjekte für erwartbare fachliche Resultate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Generic, Mapping, TypeVar

from .identifiers import BusinessId, CorrelationId

T = TypeVar("T")


class MessageSeverity(StrEnum):
    """Schweregrad einer strukturierten Ergebnisnachricht."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class ResultMessage:
    """Maschinenlesbare Meldung mit stabiler Kennung und Parametern."""

    code: BusinessId
    severity: MessageSeverity
    text: str
    parameters: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        text = self.text.strip()
        if not text:
            raise ValueError("Der Meldungstext darf nicht leer sein.")
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))

    @property
    def is_error(self) -> bool:
        return self.severity in {MessageSeverity.ERROR, MessageSeverity.CRITICAL}


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    """Unveränderliches Ergebnis für erwartbare fachliche Abläufe."""

    is_success: bool
    value: T | None
    messages: tuple[ResultMessage, ...]
    correlation_id: CorrelationId | None = None

    def __post_init__(self) -> None:
        messages = tuple(self.messages)
        object.__setattr__(self, "messages", messages)

        has_errors = any(message.is_error for message in messages)
        if self.is_success and has_errors:
            raise ValueError("Ein erfolgreiches Ergebnis darf keine Fehlermeldung enthalten.")
        if not self.is_success and not has_errors:
            raise ValueError("Ein fehlgeschlagenes Ergebnis benötigt mindestens eine Fehlermeldung.")
        if not self.is_success and self.value is not None:
            raise ValueError("Ein fehlgeschlagenes Ergebnis darf keinen gültigen Wert enthalten.")

    @classmethod
    def success(
        cls,
        value: T | None = None,
        *,
        messages: tuple[ResultMessage, ...] = (),
        correlation_id: CorrelationId | None = None,
    ) -> "Result[T]":
        return cls(True, value, messages, correlation_id)

    @classmethod
    def failure(
        cls,
        *messages: ResultMessage,
        correlation_id: CorrelationId | None = None,
    ) -> "Result[T]":
        return cls(False, None, tuple(messages), correlation_id)

    @property
    def errors(self) -> tuple[ResultMessage, ...]:
        return tuple(message for message in self.messages if message.is_error)

    @property
    def warnings(self) -> tuple[ResultMessage, ...]:
        return tuple(
            message for message in self.messages if message.severity is MessageSeverity.WARNING
        )
