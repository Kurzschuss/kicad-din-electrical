"""Read-only Korrelationsansicht für Z_Cockpit auf ProjectOS-Projektbasis."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable
from uuid import UUID

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_project_memory import ProjectOSProjectMemory


def _normalize_uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


class ZCockpitProjectCorrelationView:
    """Führt Projektkontext, Busnachrichten, Audit, Wissen und Recovery rein lesend zusammen."""

    def __init__(
        self,
        manager: DinEditorProjectManager,
        messages: Iterable[ProjectOSMessageEnvelope] | None = None,
        memory: ProjectOSProjectMemory | None = None,
    ) -> None:
        self.manager = manager
        self._messages = tuple(messages or ())
        if memory is not None and memory.project_id != manager.project_id:
            raise ValueError("project memory belongs to another project")
        self._memory = memory

    def _project_messages(self) -> list[ProjectOSMessageEnvelope]:
        project_id = self.manager.project_id
        return sorted(
            (message for message in self._messages if message.project_id == project_id),
            key=lambda message: (message.timestamp, message.message_id),
        )

    def state(self, correlation_id: str | None = None) -> dict:
        context = DinEditorProjectContext.from_manager(self.manager)
        all_project_messages = self._project_messages()
        project_messages = all_project_messages

        normalized_correlation_id = None
        if correlation_id is not None:
            normalized_correlation_id = _normalize_uuid(correlation_id, "correlation_id")
            project_messages = [m for m in project_messages if m.correlation_id == normalized_correlation_id]

        grouped: dict[str, list[dict]] = defaultdict(list)
        for message in project_messages:
            grouped[message.correlation_id].append(message.as_dict())
        correlations = [
            {"correlation_id": current_id, "messages": messages, "message_count": len(messages)}
            for current_id, messages in sorted(grouped.items())
        ]

        project_audit_entries = [
            dict(entry) for entry in self.manager.sync_log.entries
            if entry.get("project_id") == context.project_id
        ]
        audit_entries = project_audit_entries
        if normalized_correlation_id is not None:
            audit_entries = [e for e in project_audit_entries if e.get("correlation_id") == normalized_correlation_id]

        message_ids = {message.message_id for message in all_project_messages}
        correlation_linked = sum(1 for entry in project_audit_entries if entry.get("correlation_id"))
        causation_linked = sum(
            1 for entry in project_audit_entries
            if entry.get("causation_id") in message_ids
        )
        causation_unresolved = sum(
            1 for entry in project_audit_entries
            if entry.get("causation_id") and entry.get("causation_id") not in message_ids
        )

        memory_state = {
            "scope": "correlation" if normalized_correlation_id is not None else "project",
            "elements": [],
            "element_count": 0,
            "relations": [],
            "relation_count": 0,
            "causation_linked_element_count": 0,
            "causation_unresolved_element_count": 0,
            "note": (
                "Projektwissen und typisierte Beziehungen werden nur explizit gespeichert. "
                "Bei einem Vorgangsfilter werden nur Beziehungen zwischen den tatsächlich sichtbaren "
                "Wissenselementen angezeigt; fehlende Verknüpfungen werden nicht hergeleitet."
            ),
        }
        if self._memory is not None:
            raw_memory_state = self._memory.state(correlation_id=normalized_correlation_id)
            memory_items = self._memory.elements(correlation_id=normalized_correlation_id)
            memory_state["elements"] = raw_memory_state["elements"]
            memory_state["element_count"] = raw_memory_state["element_count"]
            memory_state["relations"] = raw_memory_state["relations"]
            memory_state["relation_count"] = raw_memory_state["relation_count"]
            memory_state["causation_linked_element_count"] = sum(
                1 for item in memory_items if item.causation_id in message_ids
            )
            memory_state["causation_unresolved_element_count"] = sum(
                1 for item in memory_items
                if item.causation_id and item.causation_id not in message_ids
            )

        return {
            "project": context.as_dict(),
            "filter": {"correlation_id": normalized_correlation_id},
            "correlations": correlations,
            "message_count": sum(item["message_count"] for item in correlations),
            "audit": {
                "scope": "correlation" if normalized_correlation_id is not None else "project",
                "correlation_linked": correlation_linked > 0,
                "entries": audit_entries,
                "entry_count": len(audit_entries),
                "linked_entry_count": correlation_linked,
                "unlinked_entry_count": len(project_audit_entries) - correlation_linked,
                "causation_linked_entry_count": causation_linked,
                "causation_unresolved_entry_count": causation_unresolved,
                "note": (
                    "correlation_id ordnet Audit-Einträge dem Vorgang zu; causation_id kann zusätzlich "
                    "auf die konkret auslösende ProjectOS-Nachricht verweisen. Ältere Einträge bleiben kompatibel."
                ),
            },
            "memory": memory_state,
            "recovery": self.manager.recovery_status(),
            "read_only": True,
        }