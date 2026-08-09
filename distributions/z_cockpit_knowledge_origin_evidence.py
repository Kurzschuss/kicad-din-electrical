"""Read-only Evidenzaufbereitung fuer Z_Cockpit-Wissensherkunft."""
from __future__ import annotations

from typing import Any

from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView


class ZCockpitKnowledgeOriginEvidenceView:
    """Ergaenzt gespeicherte Wissensherkunft um referenzierte Freigabenachweise."""

    def __init__(self, correlation_view: ZCockpitProjectCorrelationView) -> None:
        self.correlation_view = correlation_view

    def state(self, knowledge_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        result = self.correlation_view.explain_knowledge_origin(
            knowledge_id,
            correlation_id=correlation_id,
        )
        if not result.get("found"):
            return {
                **result,
                "evidence_references": [],
                "evidence_reference_count": 0,
            }

        nodes: dict[str, dict[str, Any]] = {}
        target = result.get("target")
        if target:
            nodes[target["knowledge_id"]] = target
        for origin in result.get("origins", []):
            for node in origin.get("nodes", []):
                nodes[node["knowledge_id"]] = node

        references = []
        for node in nodes.values():
            metadata = dict(node.get("metadata") or {})
            truth_source = metadata.get("truth_source")
            action_id = metadata.get("action_id")
            if not truth_source and not action_id:
                continue

            node_correlation = node.get("correlation_id") or metadata.get("correlation_id") or result.get("correlation_id")
            message_id = metadata.get("message_id")
            navigation = None
            if action_id and node_correlation:
                navigation = ZCockpitNavigationTarget(
                    view="approval_trace",
                    project_id=result["project_id"],
                    correlation_id=node_correlation,
                    message_ids=(message_id,) if message_id else (),
                    metadata={
                        "action_id": action_id,
                        "review_id": metadata.get("review_id"),
                        "knowledge_id": node["knowledge_id"],
                        "truth_source": truth_source,
                    },
                ).as_dict()

            references.append({
                "knowledge_id": node["knowledge_id"],
                "knowledge_type": node.get("knowledge_type"),
                "title": node.get("title"),
                "source": node.get("source"),
                "evidence_status": node.get("evidence_status"),
                "truth_source": truth_source,
                "action_id": action_id,
                "review_id": metadata.get("review_id"),
                "message_id": message_id,
                "correlation_id": node_correlation,
                "reference_id": metadata.get("reference_id"),
                "navigation_target": navigation,
            })

        references.sort(key=lambda item: (item["title"] or "", item["knowledge_id"]))
        return {
            **result,
            "evidence_references": references,
            "evidence_reference_count": len(references),
            "note": (
                f"{result.get('note', '')} Freigabe- und Nachpruefungsnachweise werden nur aus bereits "
                "gespeicherten Referenzmetadaten erklaert; fachliche Entscheidungen werden nicht neu bewertet."
            ).strip(),
            "read_only": True,
        }
