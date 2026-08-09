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
from .projectos_user_management_command_history import (
    ProjectOSUserManagementCommandHistory,
    ProjectOSUserManagementCommandRecord,
)


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementChangeTrace:
    message: ProjectOSMessageEnvelope
    audit_entry: dict[str, Any]
    command_id: str
    operation: str
    actor_user_id: str | None
    reference: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
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
        command_history: ProjectOSUserManagementCommandHistory | None = None,
    ) -> None:
        self.manager = manager
        self._uses_manager_audit_log = audit_log is None
        self.audit_log = audit_log or manager.sync_log
        self.correlation_id = _uuid(correlation_id or str(uuid4()), "correlation_id")
        self.causation_id = _uuid(causation_id, "causation_id") if causation_id is not None else None
        self.command_history = command_history or ProjectOSUserManagementCommandHistory()
        self.command_history.bind_runtime_generation(
            lambda: self.manager.user_management_runtime_generation
        )
        self.messages: list[ProjectOSMessageEnvelope] = []
        self.traces: list[ProjectOSUserManagementChangeTrace] = []
        self._previous_state = manager.user_management.as_dict()
        self._runtime_generation = manager.user_management_runtime_generation
        self._last_message_by_correlation: dict[str, str] = {}
        if self.causation_id is not None:
            self._last_message_by_correlation[self.correlation_id] = self.causation_id

    def prepare_for_change(self) -> None:
        """Richtet rein laufzeitbezogene Nachweise nach Load/Recover/Discard/New neu aus."""
        current_generation = self.manager.user_management_runtime_generation
        if current_generation == self._runtime_generation:
            return
        self.command_history.clear()
        self.messages.clear()
        self.traces.clear()
        self._previous_state = self.manager.user_management.as_dict()
        self._last_message_by_correlation.clear()
        self.correlation_id = str(uuid4())
        self.causation_id = None
        if self._uses_manager_audit_log:
            self.audit_log = self.manager.sync_log
        self._runtime_generation = current_generation

    @staticmethod
    def _changed_rows(
        previous: list[dict[str, Any]],
        current: list[dict[str, Any]],
        id_field: str,
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        before = {item[id_field]: item for item in previous}
        changed = [item for item in current if before.get(item[id_field]) != item]
        if len(changed) != 1:
            raise ValueError(f"expected exactly one changed {id_field}")
        row = changed[0]
        return before.get(row[id_field]), row

    @staticmethod
    def _command_context(event: dict[str, Any]) -> dict[str, Any] | None:
        raw = event.get("command_context")
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise ValueError("command_context must be an object")
        causation_id = raw.get("causation_id")
        related_command_id = raw.get("related_command_id")
        history_action = str(raw.get("history_action", "command")).strip().lower()
        if history_action not in {"command", "undo", "redo"}:
            raise ValueError(f"unsupported history_action: {history_action}")
        if history_action in {"undo", "redo"} and related_command_id is None:
            raise ValueError(f"{history_action} requires related_command_id")
        if history_action == "command" and related_command_id is not None:
            raise ValueError("command history_action must not define related_command_id")
        return {
            "command_id": _uuid(raw.get("command_id"), "command_id"),
            "actor_user_id": _uuid(raw.get("actor_user_id"), "actor_user_id"),
            "correlation_id": _uuid(raw.get("correlation_id"), "correlation_id"),
            "causation_id": _uuid(causation_id, "causation_id") if causation_id is not None else None,
            "history_action": history_action,
            "related_command_id": (
                _uuid(related_command_id, "related_command_id") if related_command_id is not None else None
            ),
        }

    def _change_context(
        self,
        operation: str,
    ) -> tuple[str, str | None, dict[str, Any] | None, dict[str, Any]]:
        current = self.manager.user_management.as_dict()
        previous = self._previous_state

        mapping = {
            "user_created": ("users", "user_id"),
            "user_weight_changed": ("users", "user_id"),
            "permission_assigned": ("permission_assignments", "assignment_id"),
            "project_role_assigned": ("project_roles", "role_assignment_id"),
            "project_role_activated": ("activations", "activation_id"),
            "project_role_deactivated": ("deactivations", "deactivation_id"),
            "approval_requested": ("approval_requests", "action_id"),
            "approval_recorded": ("approvals", "approval_id"),
            "post_review_completed": ("post_reviews", "review_id"),
        }
        if operation not in mapping:
            raise ValueError(f"unsupported user management operation: {operation}")

        collection, id_field = mapping[operation]
        previous_row, row = self._changed_rows(
            previous.get(collection, []),
            current.get(collection, []),
            id_field,
        )
        reference = str(row[id_field])

        if operation in {"user_created", "user_weight_changed"}:
            actor = row["user_id"]
        elif operation == "permission_assigned":
            actor = row.get("delegated_by_user_id") or row["user_id"]
        elif operation == "project_role_assigned":
            actor = row.get("assigned_by_user_id") or row["user_id"]
        elif operation in {"project_role_activated", "project_role_deactivated"}:
            actor = row.get("triggered_by_user_id") or row["user_id"]
        elif operation == "approval_requested":
            actor = row["requested_by_user_id"]
        elif operation == "approval_recorded":
            actor = row["approver_user_id"]
        else:
            actor = row["reviewer_user_id"]

        return reference, actor, previous_row, row

    @staticmethod
    def _history_values(
        operation: str,
        previous_row: dict[str, Any] | None,
        row: dict[str, Any],
    ) -> tuple[bool, dict[str, Any], dict[str, Any]]:
        if operation == "user_weight_changed" and previous_row is not None:
            return True, {"weight": previous_row["weight"]}, {"weight": row["weight"]}
        return False, {}, {}

    def __call__(self, event: dict[str, Any]) -> None:
        command_id = _uuid(event.get("command_id"), "command_id")
        operation = str(event.get("operation", "")).strip()
        project_id = _uuid(str(event.get("project_id")), "project_id")
        if project_id != self.manager.project_id:
            raise ValueError("change event belongs to another project")

        reference, derived_actor_user_id, previous_domain_payload, domain_payload = self._change_context(operation)
        command_context = self._command_context(event)
        if command_context is None:
            actor_user_id = derived_actor_user_id
            correlation_id = self.correlation_id
            causation_id = self._last_message_by_correlation.get(correlation_id)
            actor_source = "domain"
            history_action = "command"
            related_command_id = None
        else:
            if command_context["command_id"] != command_id:
                raise ValueError("command_context command_id does not match change event")
            actor_user_id = command_context["actor_user_id"]
            correlation_id = str(command_context["correlation_id"])
            causation_id = command_context["causation_id"] or self._last_message_by_correlation.get(correlation_id)
            actor_source = "command_context"
            history_action = str(command_context["history_action"])
            related_command_id = command_context["related_command_id"]

        payload = {
            "command_id": command_id,
            "operation": operation,
            "actor_user_id": actor_user_id,
            "actor_source": actor_source,
            "history_action": history_action,
            "related_command_id": related_command_id,
            "reference": reference,
            "dirty": bool(event.get("dirty")),
            "domain": domain_payload,
        }
        message = ProjectOSMessageEnvelope(
            message_type="event",
            name=f"projectos.user_management.{operation}",
            project_id=project_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            payload=payload,
        )
        audit_entry = self.audit_log.record(
            reference=reference,
            source="projectos_user_management",
            value=actor_user_id or "system",
            action=operation,
            project_id=project_id,
            command_id=command_id,
            correlation_id=correlation_id,
            causation_id=causation_id or message.message_id,
        )
        reversible, before_values, after_values = self._history_values(
            operation,
            previous_domain_payload,
            domain_payload,
        )
        self.command_history.append(
            ProjectOSUserManagementCommandRecord(
                command_id=command_id,
                project_id=project_id,
                operation=operation,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id,
                causation_id=causation_id,
                reference=reference,
                recorded_at=message.timestamp,
                reversible=reversible,
                history_action=history_action,
                related_command_id=related_command_id,
                before_values=before_values,
                after_values=after_values,
                message_id=message.message_id,
                audit_reference=audit_entry.get("reference"),
            )
        )
        trace = ProjectOSUserManagementChangeTrace(
            message=message,
            audit_entry=audit_entry,
            command_id=command_id,
            operation=operation,
            actor_user_id=actor_user_id,
            reference=reference,
        )
        self.messages.append(message)
        self.traces.append(trace)
        self._last_message_by_correlation[correlation_id] = message.message_id
        if correlation_id == self.correlation_id:
            self.causation_id = message.message_id
        self._previous_state = self.manager.user_management.as_dict()
