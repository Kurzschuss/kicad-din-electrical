"""Read-only Aufmerksamkeitsblock für die Z_Cockpit-Projektleiteransicht."""
from __future__ import annotations

from typing import Any, Iterable

from .projectos_role_approval_trace import ProjectOSRoleApprovalTrace
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTrace
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


class ZCockpitAttentionView:
    """Priorisiert bereits vorhandene Projektleiter-Nachweise ohne neue Wahrheit zu erzeugen."""

    def __init__(self, overview: ZCockpitProjectLeadOverview, approval_traces: Iterable[ProjectOSRoleApprovalTrace] | None = None, post_review_traces: Iterable[ProjectOSRolePostReviewTrace] | None = None) -> None:
        self.overview = overview
        self.approval_traces = tuple(approval_traces or ())
        self.post_review_traces = tuple(post_review_traces or ())

    def state(self, *, correlation_id: str | None = None) -> dict[str, Any]:
        overview = self.overview.state(correlation_id=correlation_id)
        items: list[dict[str, Any]] = []
        project_id = overview["project"]["project_id"]

        for work_item in overview["diagnostics"].get("work_items", []):
            affected = work_item.get("affected", {})
            correlation_ids = affected.get("correlation_ids", [])
            item_correlation_id = correlation_ids[0] if len(correlation_ids) == 1 else overview["filter"].get("correlation_id")
            target = ZCockpitNavigationTarget(view="knowledge_diagnostics", project_id=project_id, correlation_id=item_correlation_id, knowledge_ids=tuple(affected.get("knowledge_ids", [])), relation_ids=tuple(affected.get("relation_ids", [])), metadata={"diagnostic_code": work_item["code"]})
            items.append({"source": "knowledge", "code": work_item["code"], "traffic_light": work_item["traffic_light"], "priority": work_item["priority"], "summary": work_item["summary"], "recommended_action": work_item["recommended_action"], "correlation_id": item_correlation_id, "affected": affected, "detail_target": target.as_dict()})

        review_by_action = {trace.post_review_state.get("request", {}).get("action_id"): trace for trace in self.post_review_traces if trace.post_review_state.get("request", {}).get("project_id") == project_id and (correlation_id is None or trace.correlation_id == correlation_id)}
        for trace in self.approval_traces:
            request = trace.approval_state.get("request", {})
            if request.get("project_id") != project_id or (correlation_id is not None and trace.correlation_id != correlation_id):
                continue
            status = trace.approval_state.get("status")
            post_review_trace = review_by_action.get(request.get("action_id"))
            post_review_status = post_review_trace.post_review_state.get("status") if post_review_trace is not None else None
            if status == "emergency_pending_review" and post_review_status == "completed_confirmed":
                continue
            if status == "emergency_pending_review" and post_review_status == "completed_negative":
                code, light, priority = "APPROVAL_POST_REVIEW_ESCALATED", "red", 30
                summary = "Eine Notfall-Nachprüfung wurde negativ abgeschlossen und erfordert Eskalation."
                action = "Freigabevorgang öffnen, negatives Nachprüfungsergebnis und historische Rechtewirkung prüfen und die erforderliche Eskalation bearbeiten."
            elif status == "emergency_pending_review":
                code, light, priority = "APPROVAL_EMERGENCY_POST_REVIEW", "red", 30
                summary = "Eine Notfall-Rollenaktion ist vorläufig wirksam und benötigt Nachprüfung."
                action = "Freigabevorgang öffnen, Notfallgrund und Rechtewirkung prüfen und die ausstehende Nachprüfung dokumentieren."
            elif status == "rejected":
                code, light, priority = "APPROVAL_REJECTED", "yellow", 25
                summary = "Eine angeforderte Rollenaktion wurde abgelehnt und bleibt unwirksam."
                action = "Freigabevorgang und Ablehnungsgrund prüfen; bei weiterem Bedarf einen neuen fachlich begründeten Vorgang starten."
            elif status == "pending_approval":
                risk = request.get("risk_class", "low")
                code, light, priority = "APPROVAL_PENDING", "yellow", 25 if risk in {"high", "critical"} else 20
                summary = "Eine Rollenaktion wartet auf die erforderliche Freigabe."
                action = "Freigabevorgang öffnen und prüfen, welche zweite Freigabe noch fehlt."
            else:
                continue
            risk = request.get("risk_class", "low")
            target_messages = post_review_trace.messages if post_review_trace is not None else trace.messages
            target = ZCockpitNavigationTarget(view="approval_trace", project_id=project_id, correlation_id=trace.correlation_id, message_ids=tuple(item.message_id for item in target_messages), metadata={"action_id": request.get("action_id"), "approval_status": status, "post_review_status": post_review_status})
            items.append({"source": "approval", "code": code, "traffic_light": light, "priority": priority, "summary": summary, "recommended_action": action, "correlation_id": trace.correlation_id, "affected": {"action_id": request.get("action_id"), "action_type": request.get("action_type"), "risk_class": risk, "target_reference": request.get("target_reference"), "post_review_status": post_review_status}, "detail_target": target.as_dict()})

        consistency = overview.get("user_management_consistency", {})
        for issue in consistency.get("issues", []):
            target = ZCockpitNavigationTarget(view="user_management_consistency", project_id=project_id, metadata={"diagnostic_code": issue["code"]})
            items.append({
                "source": "user_management_consistency",
                "code": issue["code"],
                "traffic_light": issue["traffic_light"],
                "priority": issue["priority"],
                "summary": issue["summary"],
                "recommended_action": "Konsistenzdiagnose öffnen und die betroffene Lifecycle-Kette prüfen; die Diagnose selbst verändert keine Daten.",
                "correlation_id": None,
                "affected": issue.get("affected", {}),
                "detail_target": target.as_dict(),
            })

        persistence = overview.get("persistence", {})
        if persistence.get("bundle_migration_pending"):
            target = ZCockpitNavigationTarget(
                view="user_management_persistence",
                project_id=project_id,
                metadata={
                    "persisted_bundle_version": persistence.get("persisted_bundle_version"),
                    "migration_target_version": persistence.get("migration_target_version"),
                },
            )
            items.append({
                "source": "persistence",
                "code": "USER_MANAGEMENT_BUNDLE_MIGRATION_PENDING",
                "traffic_light": "yellow",
                "priority": 20,
                "summary": f"Das Projektbundle benötigt Migration auf Version {persistence.get('migration_target_version')}.",
                "recommended_action": "Persistenzstatus öffnen und Migration prüfen. Die Migration erfolgt erst beim expliziten Speichern des Projekts.",
                "correlation_id": None,
                "affected": {
                    "persisted_bundle_version": persistence.get("persisted_bundle_version"),
                    "migration_target_version": persistence.get("migration_target_version"),
                    "persisted_object_count": persistence.get("persisted_object_count", 0),
                },
                "detail_target": target.as_dict(),
            })
        if persistence.get("user_management_migration_pending"):
            target = ZCockpitNavigationTarget(
                view="user_management_persistence",
                project_id=project_id,
                metadata={
                    "persisted_user_management_version": persistence.get("persisted_user_management_version"),
                    "user_management_migration_target_version": persistence.get("user_management_migration_target_version"),
                },
            )
            items.append({
                "source": "persistence",
                "code": "USER_MANAGEMENT_PERSISTENCE_MIGRATION_PENDING",
                "traffic_light": "yellow",
                "priority": 20,
                "summary": (
                    "Benutzerverwaltungsdaten benötigen Migration von Persistenzversion "
                    f"{persistence.get('persisted_user_management_version')} auf "
                    f"{persistence.get('user_management_migration_target_version')}."
                ),
                "recommended_action": "Persistenzstatus öffnen und Benutzerverwaltungs-Migration prüfen. Die Aktualisierung erfolgt erst beim expliziten Speichern des Projekts.",
                "correlation_id": None,
                "affected": {
                    "persisted_user_management_version": persistence.get("persisted_user_management_version"),
                    "user_management_migration_target_version": persistence.get("user_management_migration_target_version"),
                    "persisted_object_count": persistence.get("persisted_object_count", 0),
                },
                "detail_target": target.as_dict(),
            })

        audit = overview["audit"]
        if audit["causation_unresolved_entry_count"] > 0:
            target = ZCockpitNavigationTarget(view="audit", project_id=project_id, correlation_id=overview["filter"].get("correlation_id"), audit_filter="unresolved_causation")
            items.append({"source": "audit", "code": "AUDIT_UNRESOLVED_CAUSATION", "traffic_light": "yellow", "priority": 20, "summary": f"{audit['causation_unresolved_entry_count']} Audit-Ursachenreferenzen sind nicht auflösbar.", "recommended_action": "Audit-Einträge und referenzierte ProjectOS-Nachrichten auf Vollständigkeit und korrekte causation_id prüfen.", "correlation_id": overview["filter"].get("correlation_id"), "affected": {}, "detail_target": target.as_dict()})
        if audit["unlinked_entry_count"] > 0:
            target = ZCockpitNavigationTarget(view="audit", project_id=project_id, correlation_id=overview["filter"].get("correlation_id"), audit_filter="unlinked")
            items.append({"source": "audit", "code": "AUDIT_UNLINKED", "traffic_light": "yellow", "priority": 15, "summary": f"{audit['unlinked_entry_count']} Audit-Einträge sind nicht vorgangskorreliert.", "recommended_action": "Prüfen, ob die fehlende correlation_id historisch bedingt oder fachlich nachtragbar dokumentiert werden muss.", "correlation_id": overview["filter"].get("correlation_id"), "affected": {}, "detail_target": target.as_dict()})

        recovery = overview["recovery"]
        if recovery.get("available") and recovery.get("valid") is False:
            target = ZCockpitNavigationTarget(view="recovery", project_id=project_id, correlation_id=overview["filter"].get("correlation_id"), recovery_path=recovery.get("path"))
            items.append({"source": "recovery", "code": "RECOVERY_INVALID", "traffic_light": "yellow", "priority": 20, "summary": "Eine vorhandene Recovery ist nicht verwendbar.", "recommended_action": "Recovery-Metadaten und Validierungsfehler prüfen; keine Wiederherstellung auslösen, solange can_recover=False ist.", "correlation_id": overview["filter"].get("correlation_id"), "affected": {"recovery_path": recovery.get("path")}, "detail_target": target.as_dict()})

        items.sort(key=lambda item: (-item["priority"], item["source"], item["code"]))
        return {
            "project_id": project_id,
            "correlation_id": overview["filter"].get("correlation_id"),
            "traffic_light": "red" if any(item["traffic_light"] == "red" for item in items) else overview["traffic_light"],
            "attention_required": bool(items),
            "attention_count": len(items),
            "top_priority": items[0]["priority"] if items else 0,
            "top_item": items[0] if items else None,
            "items": items,
            "read_only": True,
            "note": "Der Aufmerksamkeitsblock priorisiert vorhandene Diagnose-, Freigabe-, Persistenz-, Audit- und Recovery-Nachweise und führt keine Änderung aus.",
        }
