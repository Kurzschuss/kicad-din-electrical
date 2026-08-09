"""Korrelierter Bus-/Audit-Nachweis erfolgreicher Benutzerverwaltungsänderungen.

Der Adapter ist als on_change-Hook für ProjectOSUserManagementChangeService gedacht.
Er entscheidet keine Fachmutation selbst, sondern beschreibt ausschließlich den bereits
atomar übernommenen Zustand. Fehlgeschlagene Commands rufen den Hook nicht auf und
erzeugen damit weder Bus- noch Audit-Nachweis.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from .din_editor_sync_log import DinSyncLog
from .projectos_message_envelope import ProjectOSMessageEnvelope


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementChangeTrace:
    message: ProjectOSMessageEnvelope
    audit_entry: dict[str, Any]
    operation: str
    actor_user_id: str | None
    reference: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "actor_user_id": self.actor_user_id,
            "reference": self.reference,
            "message": self.message.as_dict(),
            "audit_entry": dict(self.audit_entry),
            "read_only_evidence": True,
        }


class ProjectOSUserManagementChangeTraceEmitter:
    """Callable Hook, der erfolgreiche Änderungen korreliert auf Bus/Audit abbildet."""

    def __init__(
        self,
        manager,
        *,
        audit_log: DinSyncLog | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> None:
        self.manager = manager
        self.audit_log = audit_log or manager.sync_log
        self.correlation_id = _uuid(correlation_id or str(uuid4()), "correlation_id")
        self.causation_id = _uuid(causation_id, "causation_id") if causation_id is not None else None
        self.messages: list[ProjectOSMessageEnvelope] = []
        self.traces: list[ProjectOSUserManagementChangeTrace] = []

    def _latest_context(self, operation: str) -> tuple[str, str | None, dict[str, Any]]:
        state = self.manager.user_management
        if operation == "user_created":
            item = state.users[-1]
            return item.user_id, item.user_id, item.as_dict()
        if operation == "user_weight_changed":
            item = state.users[-1]
            return item.user_id, item.user_id, item.as_dict()
        if operation == "permission_assigned":
            item = state.permission_assignments[-1]
            actor = item.delegated_by_user_id or item.user_id
            return item.assignment_id, actor, item.as_dict()
        if operation == "project_role_assigned":
            item = state.project_roles[-1]
            actor = item.assigned_by_user_id or item.user_id
            return item.role_assignment_id, actor, item.as_dict()
        if operation == "project_role_activated":
            item = state.activations[-1]
            actor = item.triggered_by_user_id or item.user_id
            return item.activation_id, actor, item.as_dict()
        if operation == "project_role_deactivated":
            item = state.deactivations[-1]
            actor = item.triggered_by_user_id or item.user_id
            return item.deactivation_id, actor, item.as_dict()
        if operation == "approval_requested":
            item = state.approval_requests[-1]
            return item.action_id, item.requested_by_user_id, item.as_dict()
        if operation == "approval_recorded":
            item = state.approvals[-1]
            return item.approval_id, item.approver_user_id, item.as_dict()
        if operation == "post_review_completed":
            item = state.post_reviews[-1]
            return item.review_id, item.reviewer_user_id, item.as_dict()
        raise ValueError(f"unsupported user management operation: {operation}")

    def __call__(self, event: dict[str, Any]) -> None:
        operation = str(event.get("operation", "")).strip()
        project_id = _uuid(str(event.get("project_id")), "project_id")
        if project_id != self.manager.project_id:
            raise ValueError("change event belongs to another project")
        reference, actor_user_id, domain_payload = self._latest_context(operation)

        payload = {
            "operation": operation,
            "actor_user_id": actor_user_id,
            "reference": reference,
            "dirty": bool(event.get("dirty")),
            "domain": domain_payload,
        }
        message = ProjectOSMessageEnvelope(
            message_type="event",
            name=f"projectos.user_management.{operation}",
            project_id=project_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            payload=payload,
        )
        audit_entry = self.audit_log.record(
            reference=reference,
            source="projectos_user_management",
            value=actor_user_id or "system",
            action=operation,
            project_id=project_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id or message.message_id,
        )
        trace = ProjectOSUserManagementChangeTrace(
            message=message,
            audit_entry=audit_entry,
            operation=operation,
            actor_user_id=actor_user_id,
            reference=reference,
        )
        self.messages.append(message)
        self.traces.append(trace)
        self.causation_id = message.message_id
