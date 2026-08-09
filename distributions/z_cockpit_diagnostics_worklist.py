"""Read-only Arbeitsansicht für priorisierte Wissensgraph-Diagnosen in Z_Cockpit."""
from __future__ import annotations

from typing import Any

from .projectos_knowledge_diagnostics import ProjectOSKnowledgeDiagnosticsService
from .projectos_project_memory import ProjectOSProjectMemory


_SEVERITY_LABELS = {
    "error": "Rot",
    "warning": "Gelb",
    "info": "Gelb",
}

_ROLE_FOCUS = {
    "project_lead": {
        "label": "Projektleiter",
        "focus": "Priorität, Auswirkung und notwendige fachliche Klärung",
    },
    "developer": {
        "label": "Entwickler",
        "focus": "betroffene Wissensknoten, Referenzen und technische Prüfaktion",
    },
}


class ZCockpitDiagnosticsWorklistView:
    """Bereitet Wissensdiagnosen als rein lesende Arbeitsliste für Z_Cockpit auf."""

    def __init__(
        self,
        memory: ProjectOSProjectMemory,
        *,
        known_message_ids=None,
        known_correlation_ids=None,
    ) -> None:
        self.memory = memory
        self._service = ProjectOSKnowledgeDiagnosticsService(
            memory,
            known_message_ids=known_message_ids,
            known_correlation_ids=known_correlation_ids,
        )

    def state(self, *, correlation_id: str | None = None, role: str = "project_lead") -> dict[str, Any]:
        if role not in _ROLE_FOCUS:
            raise ValueError(f"unsupported diagnostics role: {role}")

        diagnostics = self._service.analyze(correlation_id=correlation_id)
        groups = {"red": [], "yellow": [], "green": []}
        work_items = []

        for issue in diagnostics["issues"]:
            color = "red" if issue["severity"] == "error" else "yellow"
            item = {
                "code": issue["code"],
                "traffic_light": color,
                "traffic_light_label": _SEVERITY_LABELS[issue["severity"]],
                "severity": issue["severity"],
                "priority": issue["priority"],
                "count": issue["count"],
                "affected": issue["affected"],
                "recommended_action": issue["recommended_action"],
                "summary": self._summary(issue),
                "items": issue["items"],
            }
            groups[color].append(item)
            work_items.append(item)

        if not work_items:
            groups["green"].append({
                "code": "NO_DIAGNOSTIC_ISSUES",
                "traffic_light": "green",
                "traffic_light_label": "Grün",
                "severity": "none",
                "priority": 0,
                "count": 0,
                "affected": {
                    "knowledge_ids": [],
                    "relation_ids": [],
                    "correlation_ids": [],
                    "causation_ids": [],
                },
                "recommended_action": "Keine Diagnosemaßnahme erforderlich.",
                "summary": "Im sichtbaren Wissensgraphen wurden keine Diagnoseprobleme erkannt.",
                "items": [],
            })

        return {
            "project_id": diagnostics["project_id"],
            "correlation_id": diagnostics["correlation_id"],
            "role": role,
            "role_label": _ROLE_FOCUS[role]["label"],
            "role_focus": _ROLE_FOCUS[role]["focus"],
            "traffic_light": diagnostics["traffic_light"],
            "highest_severity": diagnostics["highest_severity"],
            "issue_count": diagnostics["issue_count"],
            "severity_counts": diagnostics["severity_counts"],
            "groups": groups,
            "work_items": work_items,
            "read_only": True,
            "note": (
                "Die Arbeitsansicht priorisiert ausschließlich vorhandene Diagnosen. "
                "Sie führt keine automatische Reparatur und keine fachliche Entscheidung aus."
            ),
        }

    @staticmethod
    def _summary(issue: dict[str, Any]) -> str:
        code = issue["code"]
        count = issue["count"]
        summaries = {
            "ISOLATED_KNOWLEDGE": f"{count} isolierte Wissensknoten prüfen.",
            "DUPLICATE_SEMANTIC_RELATION": f"{count} doppelte semantische Beziehungssätze prüfen.",
            "SUPERSESSION_CONFLICT": f"{count} widersprüchliche oder zyklische Ablöseketten klären.",
            "UNRESOLVED_CAUSATION": f"{count} nicht auflösbare Ursachenreferenzen prüfen.",
            "UNRESOLVED_CORRELATION": f"{count} nicht auflösbare Vorgangsreferenzen prüfen.",
        }
        return summaries.get(code, f"{count} Diagnoseeinträge für {code} prüfen.")
