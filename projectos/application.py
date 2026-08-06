"""Command- und Query-Grundlagen für die ProjectOS-Anwendungsschicht."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Callable, Generic, Mapping, Protocol, TypeVar, cast

from .identifiers import BusinessId, CorrelationId
from .results import Result

TResult = TypeVar("TResult")
TCommand = TypeVar("TCommand", bound="Command")
TQuery = TypeVar("TQuery", bound="Query")


def _normalize_type(value: str, *, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} muss Text sein.")
    normalized = value.strip().lower()
    parts = normalized.split(".")
    if len(parts) < 3 or any(not part.replace("_", "").isalnum() for part in parts):
        raise ValueError(f"{label} muss dem Schema <domäne>.<objekt>.<aktion> entsprechen.")
    return normalized


def _normalize_issued_at(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Zeitangaben benötigen einen Zeitzonenbezug.")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Command:
    """Unveränderliche Anforderung einer Zustandsänderung."""

    command_id: BusinessId
    command_type: str
    correlation_id: CorrelationId
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Mapping[str, object] = field(default_factory=dict)
    expected_revision: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "command_type", _normalize_type(self.command_type, label="Command-Typ"))
        object.__setattr__(self, "issued_at", _normalize_issued_at(self.issued_at))
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        if self.expected_revision is not None and self.expected_revision < 0:
            raise ValueError("Die erwartete Revision darf nicht negativ sein.")


@dataclass(frozen=True, slots=True)
class Query:
    """Unveränderliche, zustandsfreie Abfrage."""

    query_id: BusinessId
    query_type: str
    correlation_id: CorrelationId
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    parameters: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "query_type", _normalize_type(self.query_type, label="Query-Typ"))
        object.__setattr__(self, "requested_at", _normalize_issued_at(self.requested_at))
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))


class CommandHandler(Protocol[TCommand, TResult]):
    def __call__(self, command: TCommand) -> Result[TResult]: ...


class QueryHandler(Protocol[TQuery, TResult]):
    def __call__(self, query: TQuery) -> Result[TResult]: ...


class LocalCommandBus:
    """Synchroner Command Bus mit genau einem Handler je Command-Typ."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[Command], Result[object]]] = {}

    def register(self, command_type: str, handler: CommandHandler[Command, object]) -> None:
        normalized = _normalize_type(command_type, label="Command-Typ")
        if normalized in self._handlers:
            raise ValueError(f"Für {normalized} ist bereits ein Command-Handler registriert.")
        self._handlers[normalized] = cast(Callable[[Command], Result[object]], handler)

    def dispatch(self, command: Command) -> Result[object]:
        handler = self._handlers.get(command.command_type)
        if handler is None:
            raise LookupError(f"Kein Command-Handler für {command.command_type} registriert.")
        return handler(command)


class LocalQueryBus:
    """Synchroner Query Bus mit genau einem Handler je Query-Typ."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[Query], Result[object]]] = {}

    def register(self, query_type: str, handler: QueryHandler[Query, object]) -> None:
        normalized = _normalize_type(query_type, label="Query-Typ")
        if normalized in self._handlers:
            raise ValueError(f"Für {normalized} ist bereits ein Query-Handler registriert.")
        self._handlers[normalized] = cast(Callable[[Query], Result[object]], handler)

    def execute(self, query: Query) -> Result[object]:
        handler = self._handlers.get(query.query_type)
        if handler is None:
            raise LookupError(f"Kein Query-Handler für {query.query_type} registriert.")
        return handler(query)
