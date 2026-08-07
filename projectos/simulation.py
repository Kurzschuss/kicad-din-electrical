"""Deterministische Simulationsbausteine für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Mapping

from .events import DomainEvent
from .identifiers import BusinessId, CorrelationId


class SimulationClock:
    """Steuerbare UTC-Uhr für reproduzierbare Simulationsläufe."""

    def __init__(self, initial_time: datetime) -> None:
        self._current = self._normalize(initial_time)

    @staticmethod
    def _normalize(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("Die Simulationszeit benötigt einen Zeitzonenbezug.")
        return value.astimezone(timezone.utc)

    def now_utc(self) -> datetime:
        return self._current

    def set(self, value: datetime) -> datetime:
        normalized = self._normalize(value)
        if normalized < self._current:
            raise ValueError("Die Simulationszeit darf nicht rückwärts gesetzt werden.")
        self._current = normalized
        return self._current

    def advance(self, delta: timedelta) -> datetime:
        if delta.total_seconds() < 0:
            raise ValueError("Die Simulationszeit darf nicht rückwärts laufen.")
        self._current += delta
        return self._current


@dataclass(frozen=True, slots=True)
class SimulationContext:
    """Unveränderlicher Kontext eines isolierten Simulationslaufs."""

    simulation_id: BusinessId
    scenario_id: BusinessId
    correlation_id: CorrelationId
    started_at: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.started_at.tzinfo is None:
            raise ValueError("started_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "started_at", self.started_at.astimezone(timezone.utc))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class SimulationTraceEntry:
    """Ein einzelner, geordneter Schritt einer Simulationsspur."""

    sequence: int
    occurred_at: datetime
    category: str
    reference: str
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("Die Sequenz muss mindestens 1 sein.")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at benötigt einen Zeitzonenbezug.")
        category = self.category.strip().upper()
        reference = self.reference.strip()
        if not category or not reference:
            raise ValueError("Kategorie und Referenz dürfen nicht leer sein.")
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(timezone.utc))
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class SimulationTrace:
    """Geordnete, nur ergänzbare Spur eines Simulationslaufs."""

    def __init__(self, context: SimulationContext) -> None:
        self.context = context
        self._entries: list[SimulationTraceEntry] = []

    @property
    def entries(self) -> tuple[SimulationTraceEntry, ...]:
        return tuple(self._entries)

    def record(
        self,
        *,
        occurred_at: datetime,
        category: str,
        reference: str,
        data: Mapping[str, object] | None = None,
    ) -> SimulationTraceEntry:
        entry = SimulationTraceEntry(
            sequence=len(self._entries) + 1,
            occurred_at=occurred_at,
            category=category,
            reference=reference,
            data={} if data is None else data,
        )
        self._entries.append(entry)
        return entry

    def record_event(self, event: DomainEvent) -> SimulationTraceEntry:
        return self.record(
            occurred_at=event.occurred_at,
            category="EVENT",
            reference=event.event_type,
            data={"event_id": str(event.event_id), "payload": dict(event.payload)},
        )

    def snapshot(self) -> tuple[SimulationTraceEntry, ...]:
        return tuple(self._entries)
