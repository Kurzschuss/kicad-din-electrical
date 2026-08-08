"""Read-only Aufmerksamkeitsblock für die Z_Cockpit-Projektleiteransicht."""
from __future__ import annotations

from typing import Any

from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


class ZCockpitAttentionView:
    """Priorisiert bereits vorhandene Projektleiter-Nachweise ohne neue Wahrheit zu erzeugen."""

    def __init__(self, overview: ZCockpitProjectLeadOverview) -> None:
        self.overview = overview

    def state(self, *, correlation_id: str | None = None) -> dict[str, Any]:
        overview = self.overview.state(correlation_id=correlation_id)
        items: list[dict[str, Any]] = []

        for work_item in overview["diagnostics"].get("work_items", []):
            affected = work_item.get("affected", {})
            correlation_ids = affected.get("correlation_ids", [])
            item_correlation_id = correlation_ids[0] if len(correlation_ids) == 1 else overview["filter"].get("correlation_id")
            items.append({
                "source": "knowledge",
                "code": work_item["code"],
                "traffic_light": work_item["traffic_light"],
                "priority": work_item["priority"],
                "summary": work_item["summary"],
                "recommended_action": work_item["recommended_action"],
                "correlation_id": item_correlation_id,
                "affected": affected,
                "detail_target": {
                    "view": "knowledge_diagnostics",
                    "correlation_id": item_correlation_id,
                    "knowledge_ids": affected.get("knowledge_ids", []),
                    "relation_ids": affected.get("relation_ids", []),
                },
            })

        audit = overview["audit"]
        if audit["causation_unresolved_entry_count"] > 0:
            items.append({
                "source": "audit",
                "code": "AUDIT_UNRESOLVED_CAUSATION",
                "traffic_light": "yellow",
                "priority": 20,
                "summary": f"{audit['causation_unresolved_entry_count']} Audit-Ursachenreferenzen sind nicht auflösbar.",
                "recommended_action": "Audit-Einträge und referenzierte ProjectOS-Nachrichten auf Vollständigkeit und korrekte causation_id prüfen.",
                "correlation_id": overview["filter"].get("correlation_id"),
                "affected": {},
                "detail_target": {
                    "view": "audit",
                    "correlation_id": overview["filter"].get("correlation_id"),
                    "filter": "unresolved_causation",
                },
            })
        if audit["unlinked_entry_count"] > 0:
            items.append({
                "source": "audit",
                "code": "AUDIT_UNLINKED",
                "traffic_light": "yellow",
                "priority": 15,
                "summary": f"{audit['unlinked_entry_count']} Audit-Einträge sind nicht vorgangskorreliert.",
                "recommended_action": "Prüfen, ob die fehlende correlation_id historisch bedingt oder fachlich nachtragbar dokumentiert werden muss.",
                "correlation_id": overview["filter"].get("correlation_id"),
                "affected": {},
                "detail_target": {
                    "view": "audit",
                    "correlation_id": overview["filter"].get("correlation_id"),
                    "filter": "unlinked",
                },
            })

        recovery = overview["recovery"]
        if recovery.get("available") and recovery.get("valid") is False:
            items.append({
                "source": "recovery",
                "code": "RECOVERY_INVALID",
                "traffic_light": "yellow",
                "priority": 20,
                "summary": "Eine vorhandene Recovery ist nicht verwendbar.",
                "recommended_action": "Recovery-Metadaten und Validierungsfehler prüfen; keine Wiederherstellung auslösen, solange can_recover=False ist.",
                "correlation_id": overview["filter"].get("correlation_id"),
                "affected": {"recovery_path": recovery.get("path")},
                "detail_target": {"view": "recovery"},
            })

        items.sort(key=lambda item: (-item["priority"], item["source"], item["code"]))
        return {
            "project_id": overview["project"]["project_id"],
            "correlation_id": overview["filter"].get("correlation_id"),
            "traffic_light": overview["traffic_light"],
            "attention_required": bool(items),
            "attention_count": len(items),
            "top_priority": items[0]["priority"] if items else 0,
            "top_item": items[0] if items else None,
            "items": items,
            "read_only": True,
            "note": (
                "Der Aufmerksamkeitsblock priorisiert ausschließlich bereits vorhandene Diagnosen, Audit- und Recovery-Nachweise. "
                "Er führt keine Reparatur, Recovery oder fachliche Entscheidung aus."
            ),
        }
