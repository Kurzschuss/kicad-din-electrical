"""Read-only Konsistenzdiagnose für das ProjectOS-Projektgedächtnis."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .projectos_knowledge_status import ProjectOSKnowledgeStatusService
from .projectos_project_memory import ProjectOSProjectMemory, _normalize_optional_uuid


_DIAGNOSTIC_POLICY = {
    "ISOLATED_KNOWLEDGE": {
        "severity": "info",
        "priority": 10,
        "recommended_action": "Prüfen, ob der Wissensknoten bewusst isoliert ist oder eine explizite Beziehung fehlt.",
    },
    "DUPLICATE_SEMANTIC_RELATION": {
        "severity": "warning",
        "priority": 20,
        "recommended_action": "Doppelte semantische Beziehungen prüfen und fachlich identische Kanten gegebenenfalls bereinigen.",
    },
    "SUPERSESSION_CONFLICT": {
        "severity": "error",
        "priority": 30,
        "recommended_action": "Ablösekette fachlich prüfen; Zyklus oder mehrdeutige aktuelle Nachfolger müssen explizit aufgelöst werden.",
    },
    "UNRESOLVED_CAUSATION": {
        "severity": "warning",
        "priority": 20,
        "recommended_action": "Prüfen, ob die referenzierte verursachende Nachricht fehlt, archiviert wurde oder falsch referenziert ist.",
    },
    "UNRESOLVED_CORRELATION": {
        "severity": "warning",
        "priority": 20,
        "recommended_action": "Prüfen, ob der referenzierte Vorgang fehlt, außerhalb des sichtbaren Kontexts liegt oder falsch referenziert ist.",
    },
}


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

    @staticmethod
    def _affected_references(code: str, items: list[dict[str, Any]]) -> dict[str, list[str]]:
        knowledge_ids: set[str] = set()
        relation_ids: set[str] = set()
        correlation_ids: set[str] = set()
        causation_ids: set[str] = set()

        for item in items:
            if item.get("knowledge_id"):
                knowledge_ids.add(item["knowledge_id"])
            if item.get("source_knowledge_id"):
                knowledge_ids.add(item["source_knowledge_id"])
            if item.get("target_knowledge_id"):
                knowledge_ids.add(item["target_knowledge_id"])
            if item.get("relation_id"):
                relation_ids.add(item["relation_id"])
            if item.get("correlation_id"):
                correlation_ids.add(item["correlation_id"])
            if item.get("causation_id"):
                causation_ids.add(item["causation_id"])
            for successor in item.get("current_successors", []):
                if successor.get("knowledge_id"):
                    knowledge_ids.add(successor["knowledge_id"])
            for chain_item in item.get("supersession_chain", []):
                if chain_item.get("knowledge_id"):
                    knowledge_ids.add(chain_item["knowledge_id"])

        return {
            "knowledge_ids": sorted(knowledge_ids),
            "relation_ids": sorted(relation_ids),
            "correlation_ids": sorted(correlation_ids),
            "causation_ids": sorted(causation_ids),
        }

    @classmethod
    def _issue(cls, code: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        policy = _DIAGNOSTIC_POLICY[code]
        return {
            "code": code,
            "severity": policy["severity"],
            "priority": policy["priority"],
            "count": len(items),
            "affected": cls._affected_references(code, items),
            "recommended_action": policy["recommended_action"],
            "items": items,
        }

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
        relation_ids_by_semantic_edge: dict[tuple[str, str, str], list[str]] = {}
        for relation in relations:
            incident[relation.source_knowledge_id] += 1
            incident[relation.target_knowledge_id] += 1
            signature = (
                relation.source_knowledge_id,
                relation.target_knowledge_id,
                relation.relation_type,
            )
            semantic_edges[signature] += 1
            relation_ids_by_semantic_edge.setdefault(signature, []).append(relation.relation_id)

        isolated = [element.as_dict() for element in elements if incident[element.knowledge_id] == 0]
        duplicates = [
            {
                "source_knowledge_id": source,
                "target_knowledge_id": target,
                "relation_type": relation_type,
                "relation_ids": sorted(relation_ids_by_semantic_edge[(source, target, relation_type)]),
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
            issues.append(self._issue("ISOLATED_KNOWLEDGE", isolated))
        if duplicates:
            issues.append(self._issue("DUPLICATE_SEMANTIC_RELATION", duplicates))
        if supersession_conflicts:
            issues.append(self._issue("SUPERSESSION_CONFLICT", supersession_conflicts))
        if unresolved_causation:
            issues.append(self._issue("UNRESOLVED_CAUSATION", unresolved_causation))
        if unresolved_correlation:
            issues.append(self._issue("UNRESOLVED_CORRELATION", unresolved_correlation))

        issues.sort(key=lambda item: (-item["priority"], item["code"]))
        severity_counts = Counter(issue["severity"] for issue in issues)
        highest_severity = (
            "error" if severity_counts["error"] else
            "warning" if severity_counts["warning"] else
            "info" if severity_counts["info"] else
            "none"
        )
        traffic_light = {
            "error": "red",
            "warning": "yellow",
            "info": "yellow",
            "none": "green",
        }[highest_severity]

        return {
            "project_id": self.memory.project_id,
            "correlation_id": normalized_correlation_id,
            "element_count": len(elements),
            "relation_count": len(relations),
            "issue_count": len(issues),
            "is_consistent": not issues,
            "highest_severity": highest_severity,
            "severity_counts": {
                "error": severity_counts["error"],
                "warning": severity_counts["warning"],
                "info": severity_counts["info"],
            },
            "traffic_light": traffic_light,
            "issues": issues,
            "note": (
                "Die Diagnose ist read-only. Sie meldet ausschließlich explizit erkennbare Strukturprobleme; "
                "fehlende fachliche Beziehungen werden nicht automatisch ergänzt oder repariert."
            ),
        }