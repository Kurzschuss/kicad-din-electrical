"""Runtime-Modell für explizite ProjectOS-Wissenselemente und typisierte Beziehungen."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .din_editor_project_context import DinEditorProjectContext
from .projectos_message_envelope import ProjectOSMessageEnvelope


_ALLOWED_KNOWLEDGE_TYPES = {
    "requirement",
    "decision",
    "assumption",
    "rationale",
    "architecture_principle",
    "model_reference",
    "implementation_reference",
    "test_reference",
    "problem",
    "risk",
    "insight",
    "experience",
    "improvement",
    "review_result",
    "approval",
    "release_reference",
    "external_evidence",
    "open_question",
    "rejected_alternative",
}

_ALLOWED_STATUSES = {
    "open",
    "active",
    "confirmed",
    "superseded",
    "rejected",
    "obsolete",
    "closed",
}

_ALLOWED_RELATION_TYPES = {
    "justifies",
    "contradicts",
    "confirms",
    "refutes",
    "supersedes",
    "complements",
    "depends_on",
    "implemented_by",
    "tested_by",
    "causes",
    "affects",
    "derived_from",
    "documented_in",
    "published_in",
    "learned_from",
}


def _normalize_uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _normalize_optional_uuid(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_uuid(value, field_name)


def _normalize_timestamp(value: str | datetime | None) -> str:
    if value is None:
        timestamp = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        timestamp = value
    else:
        timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSKnowledgeElement:
    """Expliziter, referenzierbarer Wissensbaustein des Projektgedächtnisses."""

    knowledge_type: str
    title: str
    content: str
    project_id: str
    status: str = "active"
    source: str | None = None
    correlation_id: str | None = None
    causation_id: str | None = None
    evidence_status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    knowledge_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        knowledge_type = str(self.knowledge_type).strip()
        if knowledge_type not in _ALLOWED_KNOWLEDGE_TYPES:
            raise ValueError(f"unsupported knowledge_type: {knowledge_type}")
        title = str(self.title).strip()
        content = str(self.content).strip()
        status = str(self.status).strip()
        if not title:
            raise ValueError("knowledge title is required")
        if not content:
            raise ValueError("knowledge content is required")
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"unsupported knowledge status: {status}")
        if not isinstance(self.metadata, dict):
            raise ValueError("knowledge metadata must be an object")

        object.__setattr__(self, "knowledge_type", knowledge_type)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "project_id", _normalize_uuid(self.project_id, "project_id"))
        object.__setattr__(self, "knowledge_id", _normalize_uuid(self.knowledge_id, "knowledge_id"))
        object.__setattr__(self, "correlation_id", _normalize_optional_uuid(self.correlation_id, "correlation_id"))
        object.__setattr__(self, "causation_id", _normalize_optional_uuid(self.causation_id, "causation_id"))
        object.__setattr__(self, "created_at", _normalize_timestamp(self.created_at))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_project_context(
        cls,
        context: DinEditorProjectContext,
        *,
        knowledge_type: str,
        title: str,
        content: str,
        status: str = "active",
        source: str | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        evidence_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ProjectOSKnowledgeElement":
        return cls(
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            project_id=context.project_id,
            status=status,
            source=source,
            correlation_id=correlation_id,
            causation_id=causation_id,
            evidence_status=evidence_status,
            metadata=dict(metadata or {}),
        )

    @classmethod
    def from_message(
        cls,
        message: ProjectOSMessageEnvelope,
        *,
        knowledge_type: str,
        title: str,
        content: str,
        status: str = "active",
        source: str | None = None,
        evidence_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ProjectOSKnowledgeElement":
        return cls(
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            project_id=message.project_id,
            status=status,
            source=source,
            correlation_id=message.correlation_id,
            causation_id=message.message_id,
            evidence_status=evidence_status,
            metadata=dict(metadata or {}),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "knowledge_type": self.knowledge_type,
            "title": self.title,
            "content": self.content,
            "project_id": self.project_id,
            "status": self.status,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "evidence_status": self.evidence_status,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ProjectOSKnowledgeRelation:
    """Gerichtete, typisierte Beziehung zwischen zwei Wissenselementen."""

    relation_type: str
    project_id: str
    source_knowledge_id: str
    target_knowledge_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    relation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        relation_type = str(self.relation_type).strip()
        if relation_type not in _ALLOWED_RELATION_TYPES:
            raise ValueError(f"unsupported relation_type: {relation_type}")
        if not isinstance(self.metadata, dict):
            raise ValueError("relation metadata must be an object")

        project_id = _normalize_uuid(self.project_id, "project_id")
        source_id = _normalize_uuid(self.source_knowledge_id, "source_knowledge_id")
        target_id = _normalize_uuid(self.target_knowledge_id, "target_knowledge_id")
        if source_id == target_id:
            raise ValueError("knowledge relation cannot target itself")

        object.__setattr__(self, "relation_type", relation_type)
        object.__setattr__(self, "project_id", project_id)
        object.__setattr__(self, "source_knowledge_id", source_id)
        object.__setattr__(self, "target_knowledge_id", target_id)
        object.__setattr__(self, "relation_id", _normalize_uuid(self.relation_id, "relation_id"))
        object.__setattr__(self, "created_at", _normalize_timestamp(self.created_at))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def as_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "relation_type": self.relation_type,
            "project_id": self.project_id,
            "source_knowledge_id": self.source_knowledge_id,
            "target_knowledge_id": self.target_knowledge_id,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


class ProjectOSProjectMemory:
    """In-Memory-Projektgedächtnis mit expliziten Elementen und Beziehungen."""

    def __init__(
        self,
        project_id: str,
        elements: Iterable[ProjectOSKnowledgeElement] | None = None,
        relations: Iterable[ProjectOSKnowledgeRelation] | None = None,
    ):
        self.project_id = _normalize_uuid(project_id, "project_id")
        self._elements: list[ProjectOSKnowledgeElement] = []
        self._relations: list[ProjectOSKnowledgeRelation] = []
        for element in elements or ():
            self.add(element)
        for relation in relations or ():
            self.add_relation(relation)

    def add(self, element: ProjectOSKnowledgeElement) -> ProjectOSKnowledgeElement:
        if element.project_id != self.project_id:
            raise ValueError("knowledge element belongs to another project")
        if any(existing.knowledge_id == element.knowledge_id for existing in self._elements):
            raise ValueError("knowledge_id already exists")
        self._elements.append(element)
        return element

    def add_relation(self, relation: ProjectOSKnowledgeRelation) -> ProjectOSKnowledgeRelation:
        if relation.project_id != self.project_id:
            raise ValueError("knowledge relation belongs to another project")
        element_ids = {element.knowledge_id for element in self._elements}
        if relation.source_knowledge_id not in element_ids:
            raise ValueError("knowledge relation source does not exist")
        if relation.target_knowledge_id not in element_ids:
            raise ValueError("knowledge relation target does not exist")
        if any(existing.relation_id == relation.relation_id for existing in self._relations):
            raise ValueError("relation_id already exists")
        self._relations.append(relation)
        return relation

    def relate(
        self,
        source: ProjectOSKnowledgeElement | str,
        target: ProjectOSKnowledgeElement | str,
        relation_type: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ProjectOSKnowledgeRelation:
        source_id = source.knowledge_id if isinstance(source, ProjectOSKnowledgeElement) else str(source)
        target_id = target.knowledge_id if isinstance(target, ProjectOSKnowledgeElement) else str(target)
        relation = ProjectOSKnowledgeRelation(
            relation_type=relation_type,
            project_id=self.project_id,
            source_knowledge_id=source_id,
            target_knowledge_id=target_id,
            metadata=dict(metadata or {}),
        )
        return self.add_relation(relation)

    def elements(self, *, correlation_id: str | None = None) -> list[ProjectOSKnowledgeElement]:
        items = list(self._elements)
        if correlation_id is not None:
            normalized = _normalize_uuid(correlation_id, "correlation_id")
            items = [item for item in items if item.correlation_id == normalized]
        return sorted(items, key=lambda item: (item.created_at, item.knowledge_id))

    def relations(
        self,
        *,
        knowledge_id: str | None = None,
        relation_type: str | None = None,
    ) -> list[ProjectOSKnowledgeRelation]:
        items = list(self._relations)
        if knowledge_id is not None:
            normalized = _normalize_uuid(knowledge_id, "knowledge_id")
            items = [
                item for item in items
                if item.source_knowledge_id == normalized or item.target_knowledge_id == normalized
            ]
        if relation_type is not None:
            normalized_type = str(relation_type).strip()
            if normalized_type not in _ALLOWED_RELATION_TYPES:
                raise ValueError(f"unsupported relation_type: {normalized_type}")
            items = [item for item in items if item.relation_type == normalized_type]
        return sorted(items, key=lambda item: (item.created_at, item.relation_id))

    def state(self, *, correlation_id: str | None = None) -> dict[str, Any]:
        items = self.elements(correlation_id=correlation_id)
        visible_ids = {item.knowledge_id for item in items}
        relations = [
            relation for relation in self._relations
            if relation.source_knowledge_id in visible_ids and relation.target_knowledge_id in visible_ids
        ]
        return {
            "project_id": self.project_id,
            "filter": {"correlation_id": _normalize_optional_uuid(correlation_id, "correlation_id")},
            "elements": [item.as_dict() for item in items],
            "element_count": len(items),
            "relations": [item.as_dict() for item in relations],
            "relation_count": len(relations),
        }
