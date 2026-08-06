"""Lokales, deterministisches Ereignisframework für ProjectOS."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from types import MappingProxyType
from typing import Mapping

from .identifiers import BusinessId, CorrelationId, ObjectId

_EVENT_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_]*)+$")
EventHandler = Callable[["DomainEvent"], None]


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Unveränderliche fachliche Tatsache aus einer ProjectOS-Domäne."""

    event_id: ObjectId
    event_type: str
    occurred_at: datetime
    aggregate_id: ObjectId
    aggregate_business_id: BusinessId
    aggregate_revision: int
    correlation_id: CorrelationId | None = None
    payload: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        event_type = self.event_type.strip()
        if not _EVENT_TYPE_PATTERN.fullmatch(event_type):
            raise ValueError("Der Ereignistyp muss dem Schema domaene.objekt.ereignis entsprechen.")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("Der Ereigniszeitpunkt muss eine Zeitzone enthalten.")
        if self.aggregate_revision < 0:
            raise ValueError("Die Aggregatrevision darf nicht negativ sein.")
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(timezone.utc))
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


class DomainEventCollector:
    """Sammelt Ereignisse eines Aggregats bis zur erfolgreichen Übergabe."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def add(self, event: DomainEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self._events):
            raise ValueError("Ein Ereignis darf nicht doppelt gesammelt werden.")
        self._events.append(event)

    @property
    def pending(self) -> tuple[DomainEvent, ...]:
        return tuple(self._events)

    def clear(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events


class LocalEventBus:
    """Synchroner Event-Bus mit stabiler Registrierungsreihenfolge."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not _EVENT_TYPE_PATTERN.fullmatch(event_type):
            raise ValueError("Ungültiger Ereignistyp.")
        if handler in self._handlers[event_type]:
            raise ValueError("Der Handler ist für diesen Ereignistyp bereits registriert.")
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> int:
        handlers = tuple(self._handlers.get(event.event_type, ()))
        for handler in handlers:
            handler(event)
        return len(handlers)

    def publish_all(self, events: Iterable[DomainEvent]) -> int:
        return sum(self.publish(event) for event in events)
