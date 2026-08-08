"""Read-only Korrelationsansicht für Z_Cockpit auf ProjectOS-Projektbasis."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable
from uuid import UUID

from .din_editor_project_context import DinEditorProjectContext
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_message_envelope import ProjectOSMessageEnvelope


def _normalize_uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


class ZCockpitProjectCorrelationView:
    """Führt Projektkontext, Busnachrichten, Audit und Recovery rein lesend zusammen."""

    def __init__(
        self,
        manager: DinEditorProjectManager,
        messages: Iterable[ProjectOSMessageEnvelope] | None = None,
    ) -> None:
        self.manager = manager
        self._messages = tuple(messages or ())

    def _project_messages(self) -> list[ProjectOSMessageEnvelope]:
        project_id = self.manager.project_id
        return sorted(
            (message for message in self._messages if message.project_id == project_id),
            key=lambda message: (message.timestamp, message.message_id),
        )

    def state(self, correlation_id: str | None = None) -> dict:
        context = DinEditorProjectContext.from_manager(self.manager)
        project_messages = self._project_messages()

        normalized_correlation_id = None
        if correlation_id is not None:
            normalized_correlation_id = _normalize_uuid(correlation_id, "correlation_id")
            project_messages = [
                message
                for message in project_messages
                if message.correlation_id == normalized_correlation_id
            ]

        grouped: dict[str, list[dict]] = defaultdict(list)
        for message in project_messages:
            grouped[message.correlation_id].append(message.as_dict())

        correlations = [
            {
                "correlation_id": current_id,
                "messages": messages,
                "message_count": len(messages),
            }
            for current_id, messages in sorted(grouped.items())
        ]

        audit_entries = [
            dict(entry)
            for entry in self.manager.sync_log.entries
            if entry.get("project_id") == context.project_id
        ]

        return {
            "project": context.as_dict(),
            "filter": {"correlation_id": normalized_correlation_id},
            "correlations": correlations,
            "message_count": sum(item["message_count"] for item in correlations),
            "audit": {
                "scope": "project",
                "correlation_linked": False,
                "entries": audit_entries,
                "entry_count": len(audit_entries),
                "note": (
                    "Synchronisationsaudit ist derzeit über project_id korreliert; "
                    "eine correlation_id pro Audit-Eintrag ist noch nicht Teil dieses Vertrags."
                ),
            },
            "recovery": self.manager.recovery_status(),
            "read_only": True,
        }
