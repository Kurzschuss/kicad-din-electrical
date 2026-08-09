"""Read-only Projektleiter-Gesamtübersicht für Z_Cockpit."""
from __future__ import annotations

from typing import Any, Iterable

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSProjectMemory
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTrace
from .z_cockpit_diagnostics_worklist import ZCockpitDiagnosticsWorklistView
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView
from .z_cockpit_user_management_consistency import ZCockpitUserManagementConsistencyView
from .z_cockpit_user_management_persistence import ZCockpitUserManagementPersistenceView


class ZCockpitProjectLeadOverview:
    """Bündelt Projektzustand, Recovery, Persistenz, Konsistenz und Diagnose rein lesend."""

    def __init__(self, manager: DinEditorProjectManager, messages: Iterable[ProjectOSMessageEnvelope] | None = None, memory: ProjectOSProjectMemory | None = None, post_review_traces: Iterable[ProjectOSRolePostReviewTrace] | None = None) -> None:
        self.manager = manager
        self._messages = tuple(messages or ())
        self._memory = memory
        self._post_review_traces = tuple(post_review_traces or ())
        self._correlation_view = ZCockpitProjectCorrelationView(manager, messages=self._messages, memory=memory)

    def state(self, *, correlation_id: str | None = None) -> dict[str, Any]:
        correlation = self._correlation_view.state(correlation_id=correlation_id)
        recovery = correlation["recovery"]
        audit = correlation["audit"]
        persistence = ZCockpitUserManagementPersistenceView(self.manager).state()
        user_consistency = ZCockpitUserManagementConsistencyView(self.manager).state()

        diagnostics = {
            "available": self._memory is not None,
            "traffic_light": "yellow" if self._memory is None else "green",
            "issue_count": 0,
            "red_count": 0,
            "yellow_count": 0,
            "groups": {"red": [], "yellow": [], "green": []},
            "note": "Kein Projektgedächtnis verfügbar; Wissensdiagnose ist nicht vollständig bewertbar.",
        }
        if self._memory is not None:
            message_ids = {m.message_id for m in self._messages if m.project_id == self.manager.project_id}
            correlation_ids = {m.correlation_id for m in self._messages if m.project_id == self.manager.project_id}
            worklist = ZCockpitDiagnosticsWorklistView(self._memory, known_message_ids=message_ids, known_correlation_ids=correlation_ids).state(correlation_id=correlation_id, role="project_lead")
            diagnostics = {
                "available": True,
                "traffic_light": worklist["traffic_light"],
                "issue_count": worklist["issue_count"],
                "red_count": len(worklist["groups"]["red"]),
                "yellow_count": len(worklist["groups"]["yellow"]),
                "groups": worklist["groups"],
                "work_items": worklist["work_items"],
                "note": worklist["note"],
            }

        review_states = [trace.post_review_state for trace in self._post_review_traces if trace.post_review_state.get("request", {}).get("project_id") == self.manager.project_id and (correlation_id is None or trace.correlation_id == correlation_id)]
        post_reviews = {
            "open_count": sum(1 for item in review_states if item.get("status") == "pending"),
            "confirmed_count": sum(1 for item in review_states if item.get("status") == "completed_confirmed"),
            "escalated_count": sum(1 for item in review_states if item.get("status") == "completed_negative"),
            "total_count": len(review_states),
            "read_only": True,
        }

        audit_attention = audit["causation_unresolved_entry_count"] > 0 or audit["unlinked_entry_count"] > 0
        recovery_attention = bool(recovery.get("available") and recovery.get("valid") is False)
        migration_attention = bool(persistence["migration_pending"])
        post_review_red = post_reviews["open_count"] > 0 or post_reviews["escalated_count"] > 0

        if diagnostics["traffic_light"] == "red" or post_review_red or user_consistency["traffic_light"] == "red":
            traffic_light = "red"
        elif diagnostics["traffic_light"] == "yellow" or user_consistency["traffic_light"] == "yellow" or audit_attention or recovery_attention or migration_attention:
            traffic_light = "yellow"
        else:
            traffic_light = "green"

        attention_reasons = []
        if diagnostics["traffic_light"] == "red":
            attention_reasons.append("Wissensgraph enthält mindestens eine Fehlerdiagnose.")
        elif diagnostics["traffic_light"] == "yellow":
            attention_reasons.append("Wissensgraph enthält Hinweise/Warnungen oder ist nicht vollständig bewertbar.")
        if user_consistency["traffic_light"] == "red":
            attention_reasons.append("Benutzerverwaltung enthält mindestens einen semantischen Konsistenzfehler.")
        elif user_consistency["traffic_light"] == "yellow":
            attention_reasons.append("Benutzerverwaltung enthält mindestens einen Konsistenzhinweis.")
        if post_reviews["open_count"] > 0:
            attention_reasons.append("Mindestens eine Notfall-Nachprüfung ist noch offen.")
        if post_reviews["escalated_count"] > 0:
            attention_reasons.append("Mindestens eine Notfall-Nachprüfung wurde negativ abgeschlossen und erfordert Eskalation.")
        if audit["causation_unresolved_entry_count"] > 0:
            attention_reasons.append("Mindestens eine Audit-Ursachenreferenz ist nicht auflösbar.")
        if audit["unlinked_entry_count"] > 0:
            attention_reasons.append("Mindestens ein Audit-Eintrag ist noch nicht vorgangskorreliert.")
        if recovery_attention:
            attention_reasons.append("Vorhandene Recovery ist nicht verwendbar.")
        if migration_attention:
            attention_reasons.append(f"Projektbundle benötigt Migration auf Version {persistence['migration_target_version']}.")

        return {
            "project": correlation["project"],
            "filter": correlation["filter"],
            "traffic_light": traffic_light,
            "attention_required": traffic_light != "green",
            "attention_reasons": attention_reasons,
            "summary": {
                "message_count": correlation["message_count"],
                "audit_entry_count": audit["entry_count"],
                "audit_unlinked_count": audit["unlinked_entry_count"],
                "audit_unresolved_causation_count": audit["causation_unresolved_entry_count"],
                "knowledge_issue_count": diagnostics["issue_count"],
                "user_management_consistency_issue_count": user_consistency["issue_count"],
                "user_management_consistency_red_count": user_consistency["red_count"],
                "user_management_consistency_yellow_count": user_consistency["yellow_count"],
                "post_review_open_count": post_reviews["open_count"],
                "post_review_confirmed_count": post_reviews["confirmed_count"],
                "post_review_escalated_count": post_reviews["escalated_count"],
                "recovery_available": recovery.get("available", False),
                "recovery_valid": recovery.get("valid"),
                "can_recover": recovery.get("can_recover", False),
                "bundle_version": persistence["persisted_bundle_version"],
                "bundle_migration_pending": persistence["migration_pending"],
                "user_management_persisted_object_count": persistence["persisted_object_count"],
            },
            "diagnostics": diagnostics,
            "user_management_consistency": user_consistency,
            "post_reviews": post_reviews,
            "persistence": persistence,
            "audit": audit,
            "recovery": recovery,
            "correlations": correlation["correlations"],
            "read_only": True,
            "note": "Die Gesamtübersicht aggregiert ausschließlich vorhandene read-only Nachweise und führt keine Reparatur, Migration, Recovery oder Freigabe aus.",
        }
