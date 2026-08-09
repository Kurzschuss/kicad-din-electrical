"""Read-only Ableitung von Freigabe-/Nachprüfungsnachweisen in ProjectOS-Wissen.

Der Adapter erzeugt keine neue Freigabe- oder Nachprüfungsentscheidung. Er bildet
vorhandene korrelierte Trace-Nachweise als referenzierbare Wissenselemente ab.
"""
from __future__ import annotations

from typing import Iterable

from .projectos_project_memory import ProjectOSKnowledgeElement, ProjectOSProjectMemory
from .projectos_role_approval_trace import ProjectOSRoleApprovalTrace
from .projectos_role_post_review_trace import ProjectOSRolePostReviewTrace


class ProjectOSRoleKnowledgeBridge:
    def __init__(self, memory: ProjectOSProjectMemory) -> None:
        self.memory = memory

    def materialize_approval_trace(self, trace: ProjectOSRoleApprovalTrace) -> tuple[ProjectOSKnowledgeElement, ...]:
        request = trace.approval_state.get("request", {})
        if request.get("project_id") != self.memory.project_id:
            raise ValueError("approval trace belongs to another project")
        action_id = request.get("action_id")
        if not action_id:
            raise ValueError("approval trace has no action_id")
        if not trace.messages:
            raise ValueError("approval trace has no messages")

        existing = self._existing_reference_ids()
        created: list[ProjectOSKnowledgeElement] = []
        request_message = next((m for m in trace.messages if m.name.endswith("approval_requested")), trace.messages[0])
        request_ref = f"approval-request:{action_id}"
        if request_ref not in existing:
            created.append(self.memory.add(ProjectOSKnowledgeElement.from_message(
                request_message,
                knowledge_type="approval",
                title="Freigabeanforderung",
                content=f"Freigabeanforderung für Rollenaktion {action_id}.",
                status="active",
                source="projectos_role_approval_trace",
                evidence_status="referenced",
                metadata={
                    "reference_id": request_ref,
                    "action_id": action_id,
                    "action_type": request.get("action_type"),
                    "target_reference": request.get("target_reference"),
                    "risk_class": request.get("risk_class"),
                    "requested_by_user_id": request.get("requested_by_user_id"),
                    "message_id": request_message.message_id,
                    "correlation_id": trace.correlation_id,
                    "truth_source": "ProjectOSRoleActionApprovalEvaluator",
                },
            )))
            existing.add(request_ref)

        outcome_message = next((m for m in reversed(trace.messages) if m.name.endswith("approval_effectiveness_evaluated")), trace.messages[-1])
        outcome_ref = f"approval-outcome:{action_id}:{outcome_message.message_id}"
        if outcome_ref not in existing:
            status = trace.approval_state.get("status", "unknown")
            created.append(self.memory.add(ProjectOSKnowledgeElement.from_message(
                outcome_message,
                knowledge_type="approval",
                title="Freigabewirksamkeit",
                content=f"Freigabestatus der Rollenaktion {action_id}: {status}.",
                status="confirmed" if status in {"approved", "approved_not_required"} else "active",
                source="projectos_role_approval_trace",
                evidence_status="referenced",
                metadata={
                    "reference_id": outcome_ref,
                    "action_id": action_id,
                    "approval_status": status,
                    "post_review_required": trace.approval_state.get("post_review_required", False),
                    "message_id": outcome_message.message_id,
                    "correlation_id": trace.correlation_id,
                    "truth_source": "ProjectOSRoleActionApprovalEvaluator",
                },
            )))
            existing.add(outcome_ref)

        self._relate_created(created)
        return tuple(created)

    def materialize_post_review_trace(self, trace: ProjectOSRolePostReviewTrace) -> tuple[ProjectOSKnowledgeElement, ...]:
        state = trace.post_review_state
        request = state.get("request", {})
        if request.get("project_id") != self.memory.project_id:
            raise ValueError("post review trace belongs to another project")
        review = state.get("review")
        if review is None:
            return ()
        action_id = request.get("action_id")
        last_message = trace.messages[-1]
        reference_id = f"post-review:{review['review_id']}"
        if reference_id in self._existing_reference_ids():
            return ()

        element = self.memory.add(ProjectOSKnowledgeElement.from_message(
            last_message,
            knowledge_type="review_result",
            title="Notfall-Nachprüfung",
            content=(
                f"Nachprüfung der Rollenaktion {action_id}: {review['result']}. "
                f"Status: {state['status']}."
            ),
            status="confirmed" if review["result"] == "confirmed" else "active",
            source="projectos_role_post_review_trace",
            evidence_status="referenced",
            metadata={
                "reference_id": reference_id,
                "action_id": action_id,
                "review_id": review["review_id"],
                "reviewer_user_id": review["reviewer_user_id"],
                "review_result": review["result"],
                "reviewed_at": review["reviewed_at"],
                "escalation_required": state["escalation_required"],
                "historical_emergency_effect_preserved": state["historical_emergency_effect_preserved"],
                "message_id": last_message.message_id,
                "correlation_id": trace.correlation_id,
                "truth_source": "ProjectOSRoleEmergencyPostReviewEvaluator",
            },
        ))

        approval_candidates = [
            item for item in self.memory.elements(correlation_id=trace.correlation_id)
            if item.metadata.get("action_id") == action_id and item.knowledge_type == "approval"
        ]
        if approval_candidates:
            self.memory.relate(
                element,
                approval_candidates[-1],
                "derived_from",
                metadata={"action_id": action_id, "review_id": review["review_id"]},
            )
        return (element,)

    def _existing_reference_ids(self) -> set[str]:
        return {
            str(item.metadata.get("reference_id"))
            for item in self.memory.elements()
            if item.metadata.get("reference_id")
        }

    def _relate_created(self, created: Iterable[ProjectOSKnowledgeElement]) -> None:
        items = list(created)
        if len(items) >= 2:
            self.memory.relate(
                items[-1],
                items[0],
                "derived_from",
                metadata={"action_id": items[-1].metadata.get("action_id")},
            )
