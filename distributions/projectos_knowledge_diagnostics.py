"""Read-only Konsistenzdiagnose für das ProjectOS-Projektgedächtnis."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .projectos_knowledge_status import ProjectOSKnowledgeStatusService
from .projectos_project_memory import ProjectOSProjectMemory, _normalize_optional_uuid


class ProjectOSKnowledgeDiagnosticsService:
    """Meldet ausschließlich nachweisbare Inkonsistenzen im sichtbaren Wissensgraphen."""

    def __init__(
        self,
        memory: ProjectOSProjectMemory,
        *,
        known_message_ids: Iterable[str] | None = None,
        known_correlation_ids: Iterable[str] | None = None,
    ) -> None:
        self.memory = memory
        self.known_message_ids = {str(value) for value in (known_message_ids or ())}
        self.known_correlation_ids = {str(value) for value in (known_correlation_ids or ())}

    def analyze(self, *, correlation_id: str | None = None) -> dict[str, Any]:
        normalized_correlation_id = _normalize_optional_uuid(correlation_id, "correlation_id")
        elements = self.memory.elements(correlation_id=normalized_correlation_id)
        visible_ids = {element.knowledge_id for element in elements}
        relations = [
            relation for relation in self.memory.relations()
            if relation.source_knowledge_id in visible_ids and relation.target_knowledge_id in visible_ids
        ]

        incident = Counter()
        semantic_edges = Counter()
        for relation in relations:
            incident[relation.source_knowledge_id] += 1
            incident[relation.target_knowledge_id] += 1
            semantic_edges[(
                relation.source_knowledge_id,
                relation.target_knowledge_id,
                relation.relation_type,
            )] += 1

        isolated = [element.as_dict() for element in elements if incident[element.knowledge_id] == 0]
        duplicates = [
            {
                "source_knowledge_id": source,
                "target_knowledge_id": target,
                "relation_type": relation_type,
                "count": count,
            }
            for (source, target, relation_type), count in sorted(semantic_edges.items())
            if count > 1
        ]

        status_service = ProjectOSKnowledgeStatusService(self.memory)
        supersession_conflicts = []
        seen_conflicts = set()
        for element in elements:
            status = status_service.analyze(element.knowledge_id, correlation_id=normalized_correlation_id)
            if not status.get("supersession_conflict"):
                continue
            signature = (
                bool(status.get("supersession_cycle")),
                tuple(sorted(item["knowledge_id"] for item in status.get("current_successors", []))),
                tuple(sorted(item["knowledge_id"] for item in status.get("supersession_chain", []))),
            )
            if signature in seen_conflicts:
                continue
            seen_conflicts.add(signature)
            supersession_conflicts.append({
                "knowledge_id": element.knowledge_id,
                "title": element.title,
                "cycle": bool(status.get("supersession_cycle")),
                "current_successors": status.get("current_successors", []),
                "supersession_chain": status.get("supersession_chain", []),
            })

        unresolved_causation = []
        unresolved_correlation = []
        for element in elements:
            if element.causation_id and self.known_message_ids and element.causation_id not in self.known_message_ids:
                unresolved_causation.append(element.as_dict())
            if element.correlation_id and self.known_correlation_ids and element.correlation_id not in self.known_correlation_ids:
                unresolved_correlation.append(element.as_dict())

        issues = []
        if isolated:
            issues.append({"code": "ISOLATED_KNOWLEDGE", "count": len(isolated), "items": isolated})
        if duplicates:
            issues.append({"code": "DUPLICATE_SEMANTIC_RELATION", "count": len(duplicates), "items": duplicates})
        if supersession_conflicts:
            issues.append({"code": "SUPERSESSION_CONFLICT", "count": len(supersession_conflicts), "items": supersession_conflicts})
        if unresolved_causation:
            issues.append({"code": "UNRESOLVED_CAUSATION", "count": len(unresolved_causation), "items": unresolved_causation})
        if unresolved_correlation:
            issues.append({"code": "UNRESOLVED_CORRELATION", "count": len(unresolved_correlation), "items": unresolved_correlation})

        return {
            "project_id": self.memory.project_id,
            "correlation_id": normalized_correlation_id,
            "element_count": len(elements),
            "relation_count": len(relations),
            "issue_count": len(issues),
            "is_consistent": not issues,
            "issues": issues,
            "note": (
                "Die Diagnose ist read-only. Sie meldet ausschließlich explizit erkennbare Strukturprobleme; "
                "fehlende fachliche Beziehungen werden nicht automatisch ergänzt."
            ),
        }
