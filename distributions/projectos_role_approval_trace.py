"""Korrelierter Audit-/Bus-Nachweis fuer Projektfunktionsfreigaben.

Der Trace-Dienst erzeugt keine Freigabeentscheidung. Er bildet bereits vorhandene
Freigabeauftraege, Einzelentscheidungen und den vom Approval-Evaluator ermittelten
Wirksamkeitsstatus als transportneutrale Nachrichten und Audit-Eintraege ab.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from uuid import UUID, uuid4

from .din_editor_sync_log import DinSyncLog
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSRoleApprovalTrace:
    correlation_id: str
    messages: tuple[ProjectOSMessageEnvelope, ...]
    audit_entries: tuple[dict[str, Any], ...]
    approval_state: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "messages": [item.as_dict() for item in self.messages],
            "audit_entries": [dict(item) for item in self.audit_entries],
            "approval_state": dict(self.approval_state),
            "read_only_decision": True,
        }


class ProjectOSRoleApprovalTraceEmitter:
    """Erzeugt nachvollziehbare Freigabe-Spuren fuer Bus und Audit."""

    def __init__(self, audit_log: DinSyncLog | None = None) -> None:
        self.audit_log = audit_log or DinSyncLog()

    def emit(
        self,
        request: ProjectOSRoleActionApprovalRequest,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        *,
        correlation_id: str | None = None,
    ) -> ProjectOSRoleApprovalTrace:
        approval_items = tuple(approvals or ())
        state = ProjectOSRoleActionApprovalEvaluator(approval_items).evaluate(request)
        correlation = _uuid(correlation_id or str(uuid4()), "correlation_id")

        request_message = ProjectOSMessageEnvelope(
            message_type="request",
            name="projectos.role_action.approval_requested",
            project_id=request.project_id,
            correlation_id=correlation,
            payload={
                "action_id": request.action_id,
                "action_type": request.action_type,
                "target_reference": request.target_reference,
                "requested_by_user_id": request.requested_by_user_id,
                "risk_class": request.risk_class,
                "scope": request.scope,
                "emergency": request.emergency,
                "reason": request.reason,
            },
        )
        messages: list[ProjectOSMessageEnvelope] = [request_message]
        audit_entries: list[dict[str, Any]] = [
            self.audit_log.record(
                reference=request.action_id,
                source="projectos_role_approval",
                value=request.action_type,
                action="approval_requested",
                project_id=request.project_id,
                correlation_id=correlation,
                causation_id=request_message.message_id,
            )
        ]

        last_message = request_message
        for approval in sorted(approval_items, key=lambda item: (item.decided_at, item.approval_id)):
            if approval.action_id != request.action_id:
                continue
            decision_message = last_message.child(
                message_type="security_event",
                name="projectos.role_action.approval_decided",
                payload={
                    "action_id": request.action_id,
                    "approval_id": approval.approval_id,
                    "approver_user_id": approval.approver_user_id,
                    "decision": approval.decision,
                    "decided_at": approval.decided_at,
                    "comment": approval.comment,
                },
            )
            messages.append(decision_message)
            audit_entries.append(
                self.audit_log.record(
                    reference=approval.approval_id,
                    source="projectos_role_approval",
                    value=approval.decision,
                    action="approval_decided",
                    project_id=request.project_id,
                    correlation_id=correlation,
                    causation_id=last_message.message_id,
                )
            )
            last_message = decision_message

        outcome_message = last_message.child(
            message_type="security_event",
            name="projectos.role_action.approval_effectiveness_evaluated",
            payload={
                "action_id": request.action_id,
                "status": state["status"],
                "effective": state["effective"],
                "post_review_required": state["post_review_required"],
                "external_approval_count": state["external_approval_count"],
                "external_rejection_count": state["external_rejection_count"],
            },
        )
        messages.append(outcome_message)
        audit_entries.append(
            self.audit_log.record(
                reference=request.action_id,
                source="projectos_role_approval",
                value=state["status"],
                action="approval_effectiveness_evaluated",
                project_id=request.project_id,
                correlation_id=correlation,
                causation_id=last_message.message_id,
            )
        )

        return ProjectOSRoleApprovalTrace(
            correlation_id=correlation,
            messages=tuple(messages),
            audit_entries=tuple(audit_entries),
            approval_state=state,
        )
