"""Read-only Pfadermittlung und Herkunftserklärung für das ProjectOS-Projektgedächtnis."""
from __future__ import annotations

from collections import deque
from typing import Any

from .projectos_project_memory import ProjectOSProjectMemory, _normalize_optional_uuid, _normalize_uuid


class ProjectOSKnowledgePathService:
    """Ermittelt nachweisbare gerichtete Pfade im expliziten Wissensgraphen."""

    def __init__(self, memory: ProjectOSProjectMemory) -> None:
        self.memory = memory

    def find_path(
        self,
        source_knowledge_id: str,
        target_knowledge_id: str,
        *,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        source_id = _normalize_uuid(source_knowledge_id, "source_knowledge_id")
        target_id = _normalize_uuid(target_knowledge_id, "target_knowledge_id")
        normalized_correlation_id = _normalize_optional_uuid(correlation_id, "correlation_id")

        visible_elements = self.memory.elements(correlation_id=normalized_correlation_id)
        element_by_id = {element.knowledge_id: element for element in visible_elements}
        if source_id not in element_by_id:
            raise ValueError("source knowledge element is not visible in this scope")
        if target_id not in element_by_id:
            raise ValueError("target knowledge element is not visible in this scope")

        if source_id == target_id:
            element = element_by_id[source_id]
            return {
                "found": True,
                "project_id": self.memory.project_id,
                "correlation_id": normalized_correlation_id,
                "source_knowledge_id": source_id,
                "target_knowledge_id": target_id,
                "nodes": [element.as_dict()],
                "relations": [],
                "hop_count": 0,
                "explanation": element.title,
            }

        visible_ids = set(element_by_id)
        relations = [
            relation for relation in self.memory.relations()
            if relation.source_knowledge_id in visible_ids and relation.target_knowledge_id in visible_ids
        ]
        outgoing: dict[str, list] = {}
        for relation in relations:
            outgoing.setdefault(relation.source_knowledge_id, []).append(relation)
        for items in outgoing.values():
            items.sort(key=lambda relation: (relation.created_at, relation.relation_id))

        queue = deque([source_id])
        previous: dict[str, tuple[str, object]] = {}
        visited = {source_id}

        while queue:
            current = queue.popleft()
            for relation in outgoing.get(current, []):
                target = relation.target_knowledge_id
                if target in visited:
                    continue
                visited.add(target)
                previous[target] = (current, relation)
                if target == target_id:
                    queue.clear()
                    break
                queue.append(target)

        if target_id not in previous:
            return {
                "found": False,
                "project_id": self.memory.project_id,
                "correlation_id": normalized_correlation_id,
                "source_knowledge_id": source_id,
                "target_knowledge_id": target_id,
                "nodes": [],
                "relations": [],
                "hop_count": None,
                "explanation": None,
            }

        relation_path = []
        node_ids = [target_id]
        current = target_id
        while current != source_id:
            prior, relation = previous[current]
            relation_path.append(relation)
            node_ids.append(prior)
            current = prior
        relation_path.reverse()
        node_ids.reverse()

        nodes = [element_by_id[knowledge_id] for knowledge_id in node_ids]
        explanation_parts = [nodes[0].title]
        for relation, node in zip(relation_path, nodes[1:]):
            explanation_parts.append(f"--{relation.relation_type}--> {node.title}")

        return {
            "found": True,
            "project_id": self.memory.project_id,
            "correlation_id": normalized_correlation_id,
            "source_knowledge_id": source_id,
            "target_knowledge_id": target_id,
            "nodes": [node.as_dict() for node in nodes],
            "relations": [relation.as_dict() for relation in relation_path],
            "hop_count": len(relation_path),
            "explanation": " ".join(explanation_parts),
        }
