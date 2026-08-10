"""Versionierte Persistenz für ProjectOS-Projektgedächtnis und Diagnosekontext.

Persistiert werden ausschließlich die fachlichen Quellen der Laufzeitdiagnose:
Wissenselemente, Beziehungen sowie bekannte Message-/Correlation-IDs. Abgeleitete
Diagnoseergebnisse werden bewusst nicht gespeichert, sondern reproduzierbar neu
berechnet.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import UUID

from .din_editor_project_bundle import _load_json, _save_json_atomic
from .projectos_project_memory import (
    ProjectOSKnowledgeElement,
    ProjectOSKnowledgeRelation,
    ProjectOSProjectMemory,
)

PROJECT_MEMORY_PERSISTENCE_VERSION = 1


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _uuid_tuple(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    normalized = tuple(sorted({_uuid(value, field_name) for value in values}))
    return normalized


def _timestamp(value: str | datetime | None) -> str:
    if value is None:
        current = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        current = value
    else:
        current = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("saved_at must include a timezone")
    return current.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSProjectMemoryState:
    """Persistierbarer Quellzustand für Wissensgraph-Diagnosen."""

    memory: ProjectOSProjectMemory
    known_message_ids: tuple[str, ...] = ()
    known_correlation_ids: tuple[str, ...] = ()
    saved_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.memory, ProjectOSProjectMemory):
            raise TypeError("memory must be ProjectOSProjectMemory")
        object.__setattr__(self, "known_message_ids", _uuid_tuple(self.known_message_ids, "known_message_id"))
        object.__setattr__(self, "known_correlation_ids", _uuid_tuple(self.known_correlation_ids, "known_correlation_id"))
        object.__setattr__(self, "saved_at", _timestamp(self.saved_at or None))

    @property
    def project_id(self) -> str:
        return self.memory.project_id

    @property
    def element_count(self) -> int:
        return len(self.memory.elements())

    @property
    def relation_count(self) -> int:
        return len(self.memory.relations())

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": PROJECT_MEMORY_PERSISTENCE_VERSION,
            "project_id": self.project_id,
            "saved_at": self.saved_at,
            "known_message_ids": list(self.known_message_ids),
            "known_correlation_ids": list(self.known_correlation_ids),
            "elements": [item.as_dict() for item in self.memory.elements()],
            "relations": [item.as_dict() for item in self.memory.relations()],
            "derived_not_persisted": [
                "knowledge_diagnostics",
                "z_cockpit_diagnostics_worklist",
                "traffic_light",
                "severity_counts",
                "recommended_actions",
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectOSProjectMemoryState":
        if not isinstance(data, dict):
            raise ValueError("project memory state must be an object")
        if data.get("version") != PROJECT_MEMORY_PERSISTENCE_VERSION:
            raise ValueError("unsupported project memory persistence version")
        project_id = _uuid(data.get("project_id"), "project_id")

        def rows(name: str) -> list[dict[str, Any]]:
            value = data.get(name, [])
            if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
                raise ValueError(f"{name} must be a list of objects")
            return value

        elements = tuple(ProjectOSKnowledgeElement(**item) for item in rows("elements"))
        memory = ProjectOSProjectMemory(project_id, elements=elements)
        for relation_data in rows("relations"):
            memory.add_relation(ProjectOSKnowledgeRelation(**relation_data))

        message_ids = data.get("known_message_ids", [])
        correlation_ids = data.get("known_correlation_ids", [])
        if not isinstance(message_ids, list):
            raise ValueError("known_message_ids must be a list")
        if not isinstance(correlation_ids, list):
            raise ValueError("known_correlation_ids must be a list")
        return cls(
            memory=memory,
            known_message_ids=tuple(str(value) for value in message_ids),
            known_correlation_ids=tuple(str(value) for value in correlation_ids),
            saved_at=str(data.get("saved_at") or ""),
        )


def snapshot_project_memory(
    memory: ProjectOSProjectMemory,
    *,
    known_message_ids: Iterable[str] = (),
    known_correlation_ids: Iterable[str] = (),
    saved_at: str | datetime | None = None,
) -> ProjectOSProjectMemoryState:
    """Erzeugt einen persistierbaren Snapshot ohne Diagnoseableitungen."""
    return ProjectOSProjectMemoryState(
        memory=memory,
        known_message_ids=tuple(known_message_ids),
        known_correlation_ids=tuple(known_correlation_ids),
        saved_at=_timestamp(saved_at),
    )


def save_project_memory_state(
    path: str | Path,
    memory: ProjectOSProjectMemory,
    *,
    known_message_ids: Iterable[str] = (),
    known_correlation_ids: Iterable[str] = (),
    saved_at: str | datetime | None = None,
) -> Path:
    """Speichert den Wissensgraphzustand atomar als versioniertes JSON."""
    state = snapshot_project_memory(
        memory,
        known_message_ids=known_message_ids,
        known_correlation_ids=known_correlation_ids,
        saved_at=saved_at,
    )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return _save_json_atomic(state.as_dict(), target)


def load_project_memory_state(path: str | Path) -> ProjectOSProjectMemoryState:
    """Lädt und validiert einen persistierten Wissensgraphzustand."""
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise ValueError("project memory state must be an object")
    return ProjectOSProjectMemoryState.from_dict(raw)
