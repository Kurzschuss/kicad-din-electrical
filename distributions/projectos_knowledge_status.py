"""Read-only Statusanalyse für Widerspruchs- und Ablöseketten im ProjectOS-Wissensgraphen."""
from __future__ import annotations

from collections import deque
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

        replacement_outgoing: dict[str, list] = {}
        for relation in relations:
            if relation.relation_type == "supersedes":
                replacement_outgoing.setdefault(relation.target_knowledge_id, []).append(relation)
        for items in replacement_outgoing.values():
            items.sort(key=lambda relation: (relation.created_at, relation.relation_id))

        chains: list[dict[str, Any]] = []
        queue = deque([(target_id, [target_id], [])])
        cycle_detected = False
        while queue:
            current, node_ids, relation_path = queue.popleft()
            next_relations = replacement_outgoing.get(current, [])
            if not next_relations:
                chains.append({"node_ids": node_ids, "relations": relation_path})
                continue
            for relation in next_relations:
                successor = relation.source_knowledge_id
                if successor in node_ids:
                    cycle_detected = True
                    chains.append({
                        "node_ids": node_ids + [successor],
                        "relations": relation_path + [relation],
                        "cycle": True,
                    })
                    continue
                queue.append((successor, node_ids + [successor], relation_path + [relation]))

        terminal_ids = sorted({
            chain["node_ids"][-1]
            for chain in chains
            if not chain.get("cycle") and chain["node_ids"][-1] in element_by_id
        })
        ambiguous_successor = len(terminal_ids) > 1
        current_successor = element_by_id[terminal_ids[0]].as_dict() if len(terminal_ids) == 1 else None

        declared_status = element_by_id[target_id].status
        if cycle_detected or ambiguous_successor:
            graph_status = "supersession_conflict"
        elif superseded_by:
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

        chain_payload = []
        for chain in chains:
            chain_payload.append({
                "nodes": [element_by_id[node_id].as_dict() for node_id in chain["node_ids"] if node_id in element_by_id],
                "relations": [relation.as_dict() for relation in chain["relations"]],
                "cycle": bool(chain.get("cycle")),
                "hop_count": len(chain["relations"]),
            })

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
            "supersession_chains": chain_payload,
            "terminal_successor_count": len(terminal_ids),
            "terminal_successors": [element_by_id[item].as_dict() for item in terminal_ids],
            "current_successor": current_successor,
            "supersession_cycle_detected": cycle_detected,
            "supersession_ambiguous": ambiguous_successor,
            "note": (
                "graph_status wird ausschließlich aus expliziten supersedes-, contradicts- und refutes-Beziehungen "
                "im sichtbaren Wissensgraphen abgeleitet. Mehrstufige Ablöseketten werden bis zu expliziten "
                "Endknoten verfolgt; Zyklen oder mehrere Endnachfolger werden als Konflikt markiert. "
                "Der deklarierte Status des Wissenselements wird nicht verändert."
            ),
        }