"""Read-only Statusanalyse für Widerspruchs- und Ablöseketten im ProjectOS-Wissensgraphen."""
from __future__ import annotations

from typing import Any

from .projectos_project_memory import ProjectOSProjectMemory, _normalize_optional_uuid, _normalize_uuid


class ProjectOSKnowledgeStatusService:
    """Erklärt den sichtbaren Status eines Wissenselements ausschließlich aus expliziten Beziehungen."""

    def __init__(self, memory: ProjectOSProjectMemory) -> None:
        self.memory = memory

    def analyze(
        self,
        knowledge_id: str,
        *,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        target_id = _normalize_uuid(knowledge_id, "knowledge_id")
        normalized_correlation_id = _normalize_optional_uuid(correlation_id, "correlation_id")
        elements = self.memory.elements(correlation_id=normalized_correlation_id)
        element_by_id = {element.knowledge_id: element for element in elements}
        if target_id not in element_by_id:
            raise ValueError("knowledge element is not visible in this scope")

        visible_ids = set(element_by_id)
        relations = [
            relation for relation in self.memory.relations()
            if relation.source_knowledge_id in visible_ids and relation.target_knowledge_id in visible_ids
        ]

        superseded_by = [
            relation for relation in relations
            if relation.relation_type == "supersedes" and relation.target_knowledge_id == target_id
        ]
        supersedes = [
            relation for relation in relations
            if relation.relation_type == "supersedes" and relation.source_knowledge_id == target_id
        ]
        conflicts = [
            relation for relation in relations
            if relation.relation_type in {"contradicts", "refutes"}
            and (relation.source_knowledge_id == target_id or relation.target_knowledge_id == target_id)
        ]

        declared_status = element_by_id[target_id].status
        if superseded_by:
            graph_status = "superseded"
        elif conflicts:
            graph_status = "conflicted"
        else:
            graph_status = "unchallenged"

        def describe_relation(relation):
            other_id = (
                relation.source_knowledge_id
                if relation.target_knowledge_id == target_id
                else relation.target_knowledge_id
            )
            return {
                "relation": relation.as_dict(),
                "other": element_by_id[other_id].as_dict(),
            }

        return {
            "project_id": self.memory.project_id,
            "correlation_id": normalized_correlation_id,
            "knowledge_id": target_id,
            "element": element_by_id[target_id].as_dict(),
            "declared_status": declared_status,
            "graph_status": graph_status,
            "is_superseded": bool(superseded_by),
            "has_conflicts": bool(conflicts),
            "superseded_by": [describe_relation(item) for item in superseded_by],
            "supersedes": [describe_relation(item) for item in supersedes],
            "conflicts": [describe_relation(item) for item in conflicts],
            "note": (
                "graph_status wird ausschließlich aus expliziten supersedes-, contradicts- und refutes-Beziehungen "
                "im sichtbaren Wissensgraphen abgeleitet. Der deklarierte Status des Wissenselements wird nicht verändert."
            ),
        }
