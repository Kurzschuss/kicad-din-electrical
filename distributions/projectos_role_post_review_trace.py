"""Korrelierter Audit-/Bus-Nachweis fuer den Abschluss von Notfall-Nachpruefungen."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .din_editor_sync_log import DinSyncLog
from .projectos_message_envelope import ProjectOSMessageEnvelope
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTrace
from .projectos_role_post_review import (
    ProjectOSRoleEmergencyPostReview,
    ProjectOSRoleEmergencyPostReviewEvaluator,
)


@dataclass(frozen=True)
class ProjectOSRolePostReviewTrace:
    correlation_id: str
    messages: tuple[ProjectOSMessageEnvelope, ...]
    audit_entries: tuple[dict[str, Any], ...]
    post_review_state: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "messages": [item.as_dict() for item in self.messages],
            "audit_entries": [dict(item) for item in self.audit_entries],
            "post_review_state": dict(self.post_review_state),
            "read_only_decision": True,
        }


class ProjectOSRolePostReviewTraceEmitter:
    """Haengt den Nachpruefungsabschluss an einen bestehenden Freigabevorgang an."""

    def __init__(self, audit_log: DinSyncLog | None = None) -> None:
        self.audit_log = audit_log or DinSyncLog()

    def emit(
        self,
        approval_trace: ProjectOSRoleApprovalTrace,
        request: ProjectOSRoleActionApprovalRequest,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        reviews: Iterable[ProjectOSRoleEmergencyPostReview] | None = None,
    ) -> ProjectOSRolePostReviewTrace:
        if approval_trace.approval_state["request"]["action_id"] != request.action_id:
            raise ValueError("approval trace belongs to another action_id")
        if not approval_trace.messages:
            raise ValueError("approval trace must contain messages")
        if any(item.project_id != request.project_id for item in approval_trace.messages):
            raise ValueError("approval trace belongs to another project_id")

        state = ProjectOSRoleEmergencyPostReviewEvaluator(approvals, reviews).evaluate(request)
        messages = list(approval_trace.messages)
        audit_entries = list(approval_trace.audit_entries)

        review = state.get("review")
        if review is None:
            return ProjectOSRolePostReviewTrace(
                correlation_id=approval_trace.correlation_id,
                messages=tuple(messages),
                audit_entries=tuple(audit_entries),
                post_review_state=state,
            )

        last_message = messages[-1]
        event_name = (
            "projectos.role_action.post_review_escalated"
            if state["escalation_required"]
            else "projectos.role_action.post_review_completed"
        )
        action_name = "post_review_escalated" if state["escalation_required"] else "post_review_completed"
        post_review_message = last_message.child(
            message_type="security_event",
            name=event_name,
            payload={
                "action_id": request.action_id,
                "review_id": review["review_id"],
                "reviewer_user_id": review["reviewer_user_id"],
                "result": review["result"],
                "reviewed_at": review["reviewed_at"],
                "comment": review["comment"],
                "status": state["status"],
                "escalation_required": state["escalation_required"],
                "historical_emergency_effect_preserved": state["historical_emergency_effect_preserved"],
            },
        )
        messages.append(post_review_message)
        audit_entries.append(
            self.audit_log.record(
                reference=review["review_id"],
                source="projectos_role_post_review",
                value=review["result"],
                action=action_name,
                project_id=request.project_id,
                correlation_id=approval_trace.correlation_id,
                causation_id=last_message.message_id,
            )
        )
        return ProjectOSRolePostReviewTrace(
            correlation_id=approval_trace.correlation_id,
            messages=tuple(messages),
            audit_entries=tuple(audit_entries),
            post_review_state=state,
        )
