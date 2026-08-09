"""Read-only Auflösung validierter Z_Cockpit-Navigationsziele."""
from __future__ import annotations

from typing import Any, Iterable

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSProjectMemory
from .z_cockpit_diagnostics_worklist import ZCockpitDiagnosticsWorklistView
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_context import ZCockpitNavigationContext
from .z_cockpit_project_correlation import ZCockpitProjectCorrelationView
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview
from .z_cockpit_role_approval_trace import ZCockpitRoleApprovalTraceView


class ZCockpitNavigationResolver:
    """Löst UI-neutrale Navigationsziele in bestehende read-only Z_Cockpit-Sichten auf."""

    def __init__(
        self,
        manager: DinEditorProjectManager,
        messages: Iterable[ProjectOSMessageEnvelope] | None = None,
        memory: ProjectOSProjectMemory | None = None,
    ) -> None:
        self.manager = manager
        self.messages = tuple(messages or ())
        self.memory = memory
        self._correlation_view = ZCockpitProjectCorrelationView(
            manager,
            messages=self.messages,
            memory=memory,
        )

    def resolve_context(self, context: ZCockpitNavigationContext) -> dict[str, Any]:
        """Löst das aktuelle Ziel auf und erhält Herkunft sowie Rücksprungkontext."""
        resolved = self.resolve(context.current)
        return {
            **resolved,
            "navigation": context.as_dict(),
        }

    def resolve(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        if target.project_id != self.manager.project_id:
            raise ValueError("navigation target belongs to another project")

        handlers = {
            "project_overview": self._project_overview,
            "correlation": self._correlation,
            "audit": self._audit,
            "knowledge_diagnostics": self._knowledge_diagnostics,
            "knowledge_element": self._knowledge_element,
            "knowledge_path": self._knowledge_path,
            "knowledge_origin": self._knowledge_origin,
            "recovery": self._recovery,
            "approval_trace": self._approval_trace,
        }
        payload = handlers[target.view](target)
        return {
            "target": target.as_dict(),
            "resolved_view": target.view,
            "payload": payload,
            "read_only": True,
        }

    def _project_overview(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        return ZCockpitProjectLeadOverview(
            self.manager,
            messages=self.messages,
            memory=self.memory,
        ).state(correlation_id=target.correlation_id)

    def _correlation(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        if target.correlation_id is None:
            raise ValueError("correlation navigation requires correlation_id")
        return self._correlation_view.state(correlation_id=target.correlation_id)

    def _audit(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        audit = self._correlation_view.state(correlation_id=target.correlation_id)["audit"]
        entries = list(audit["entries"])
        if target.audit_filter == "unresolved_causation":
            message_ids = {
                message.message_id for message in self.messages
                if message.project_id == self.manager.project_id
            }
            entries = [
                entry for entry in entries
                if entry.get("causation_id") and entry.get("causation_id") not in message_ids
            ]
        elif target.audit_filter == "unlinked":
            entries = [entry for entry in entries if not entry.get("correlation_id")]
        elif target.audit_filter not in {None, "all"}:
            raise ValueError(f"unsupported audit_filter: {target.audit_filter}")
        return {
            **audit,
            "entries": entries,
            "entry_count": len(entries),
            "applied_filter": target.audit_filter,
        }

    def _require_memory(self) -> ProjectOSProjectMemory:
        if self.memory is None:
            raise ValueError("navigation target requires project memory")
        return self.memory

    def _knowledge_diagnostics(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        memory = self._require_memory()
        message_ids = {
            message.message_id for message in self.messages
            if message.project_id == self.manager.project_id
        }
        correlation_ids = {
            message.correlation_id for message in self.messages
            if message.project_id == self.manager.project_id
        }
        state = ZCockpitDiagnosticsWorklistView(
            memory,
            known_message_ids=message_ids,
            known_correlation_ids=correlation_ids,
        ).state(correlation_id=target.correlation_id, role="project_lead")
        state["focus"] = {
            "knowledge_ids": list(target.knowledge_ids),
            "relation_ids": list(target.relation_ids),
        }
        return state

    def _knowledge_element(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        memory = self._require_memory()
        knowledge_id = target.knowledge_ids[0]
        visible = {
            element.knowledge_id: element
            for element in memory.elements(correlation_id=target.correlation_id)
        }
        if knowledge_id not in visible:
            raise ValueError("knowledge element is not visible in this scope")
        return {
            "element": visible[knowledge_id].as_dict(),
            "relations": [relation.as_dict() for relation in memory.relations(knowledge_id=knowledge_id)],
            "correlation_id": target.correlation_id,
            "read_only": True,
        }

    def _knowledge_path(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        self._require_memory()
        return self._correlation_view.explain_knowledge_path(
            target.knowledge_ids[0],
            target.knowledge_ids[1],
            correlation_id=target.correlation_id,
        )

    def _knowledge_origin(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        self._require_memory()
        return self._correlation_view.explain_knowledge_origin(
            target.knowledge_ids[0],
            correlation_id=target.correlation_id,
        )

    def _recovery(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        state = self.manager.recovery_status()
        if target.recovery_path is not None and state.get("path") != target.recovery_path:
            raise ValueError("recovery navigation path does not match current recovery")
        return state

    def _approval_trace(self, target: ZCockpitNavigationTarget) -> dict[str, Any]:
        if target.correlation_id is None:
            raise ValueError("approval_trace navigation requires correlation_id")
        action_id = target.metadata.get("action_id")
        return ZCockpitRoleApprovalTraceView(
            messages=self.messages,
            audit_entries=self.manager.sync_log.export(),
        ).state(
            project_id=self.manager.project_id,
            correlation_id=target.correlation_id,
            action_id=action_id,
        )
