"""Read-only Z_Cockpit-Sicht auf korrelierte Rollenfreigabevorgaenge."""
from __future__ import annotations

from typing import Any, Iterable
from uuid import UUID

from .projectos_message_envelope import ProjectOSMessageEnvelope


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


_EVENT_LABELS = {
    "projectos.role_action.approval_requested": "Freigabe angefordert",
    "projectos.role_action.approval_decided": "Freigabe entschieden",
    "projectos.role_action.approval_effectiveness_evaluated": "Wirksamkeit bewertet",
    "projectos.role_action.post_review_completed": "Notfall-Nachpruefung abgeschlossen",
    "projectos.role_action.post_review_escalated": "Notfall-Nachpruefung eskaliert",
}

_STATUS_LABELS = {
    "approval_missing": "Freigabeauftrag fehlt",
    "pending_approval": "Freigabe ausstehend",
    "approved": "Freigegeben",
    "approved_not_required": "Keine zweite Freigabe erforderlich",
    "rejected": "Abgelehnt",
    "emergency_pending_review": "Notfall vorlaeufig wirksam – Nachpruefung erforderlich",
    "completed_confirmed": "Notfall-Nachpruefung abgeschlossen – bestaetigt",
    "completed_negative": "Notfall-Nachpruefung abgeschlossen – Eskalation erforderlich",
}


class ZCockpitRoleApprovalTraceView:
    """Erklaert einen Freigabevorgang aus bereits vorhandenen Bus-/Audit-Nachweisen."""

    def __init__(
        self,
        *,
        messages: Iterable[ProjectOSMessageEnvelope] | None = None,
        audit_entries: Iterable[dict[str, Any]] | None = None,
    ) -> None:
        self.messages = tuple(messages or ())
        self.audit_entries = tuple(dict(item) for item in (audit_entries or ()))

    def state(self, *, project_id: str, correlation_id: str, action_id: str) -> dict[str, Any]:
        project = _uuid(project_id, "project_id")
        correlation = _uuid(correlation_id, "correlation_id")
        action = _uuid(action_id, "action_id")

        messages = [
            item for item in self.messages
            if item.project_id == project
            and item.correlation_id == correlation
            and item.payload.get("action_id") == action
            and item.name in _EVENT_LABELS
        ]
        messages.sort(key=lambda item: (item.timestamp, item.message_id))
        audits = [
            dict(item) for item in self.audit_entries
            if item.get("project_id") == project
            and item.get("correlation_id") == correlation
            and (
                item.get("reference") == action
                or item.get("action") in {"approval_decided", "post_review_completed", "post_review_escalated"}
            )
            and item.get("source") in {"projectos_role_approval", "projectos_role_post_review"}
        ]

        request = next((item for item in messages if item.name.endswith("approval_requested")), None)
        outcome = next((item for item in reversed(messages) if item.name.endswith("approval_effectiveness_evaluated")), None)
        decisions = [item for item in messages if item.name.endswith("approval_decided")]
        post_review = next(
            (
                item for item in reversed(messages)
                if item.name.endswith("post_review_completed") or item.name.endswith("post_review_escalated")
            ),
            None,
        )

        timeline = [
            {
                "message_id": item.message_id,
                "causation_id": item.causation_id,
                "timestamp": item.timestamp,
                "event": item.name,
                "label": _EVENT_LABELS[item.name],
                "payload": dict(item.payload),
            }
            for item in messages
        ]

        approval_status = outcome.payload.get("status") if outcome is not None else "pending_approval"
        if post_review is not None:
            status = post_review.payload.get("status", approval_status)
            post_review_required = False
            escalation_required = bool(post_review.payload.get("escalation_required"))
            post_review_completed = True
        else:
            status = approval_status
            post_review_required = bool(outcome and outcome.payload.get("post_review_required"))
            escalation_required = False
            post_review_completed = False

        return {
            "project_id": project,
            "correlation_id": correlation,
            "action_id": action,
            "found": request is not None,
            "request": dict(request.payload) if request is not None else None,
            "decisions": [dict(item.payload) for item in decisions],
            "outcome": dict(outcome.payload) if outcome is not None else None,
            "post_review": dict(post_review.payload) if post_review is not None else None,
            "approval_status": approval_status,
            "status": status,
            "status_label": _STATUS_LABELS.get(status, status),
            "post_review_required": post_review_required,
            "post_review_completed": post_review_completed,
            "escalation_required": escalation_required,
            "attention_required": (
                status in {"approval_missing", "pending_approval", "rejected", "emergency_pending_review", "completed_negative"}
            ),
            "timeline": timeline,
            "audit_entries": audits,
            "message_count": len(messages),
            "audit_entry_count": len(audits),
            "read_only": True,
            "note": "Die Ansicht bildet ausschliesslich vorhandene korrelierte Bus- und Audit-Nachweise ab und erzeugt keine Freigabe- oder Nachpruefungsentscheidung.",
        }
