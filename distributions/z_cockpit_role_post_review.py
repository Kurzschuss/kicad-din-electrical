"""Read-only Z_Cockpit-Sicht fuer Notfall-Nachpruefungen."""
from __future__ import annotations

from typing import Any, Iterable

from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_post_review import (
    ProjectOSRoleEmergencyPostReview,
    ProjectOSRoleEmergencyPostReviewEvaluator,
)

_STATUS_LABELS = {
    "not_required": "Keine Notfall-Nachprüfung erforderlich",
    "pending": "Notfall-Nachprüfung ausstehend",
    "completed_confirmed": "Notfall-Nachprüfung abgeschlossen – bestätigt",
    "completed_negative": "Notfall-Nachprüfung abgeschlossen – Eskalation erforderlich",
}


class ZCockpitRoleEmergencyPostReviewView:
    def __init__(
        self,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        reviews: Iterable[ProjectOSRoleEmergencyPostReview] | None = None,
    ) -> None:
        self._evaluator = ProjectOSRoleEmergencyPostReviewEvaluator(approvals, reviews)

    def state(self, request: ProjectOSRoleActionApprovalRequest) -> dict[str, Any]:
        result = self._evaluator.evaluate(request)
        return {
            **result,
            "status_label": _STATUS_LABELS[result["status"]],
            "traffic_light": self._traffic_light(result),
            "attention_required": result["post_review_required"] or result["escalation_required"],
            "explanation": self._explanation(result),
            "read_only": True,
        }

    @staticmethod
    def _traffic_light(result: dict[str, Any]) -> str:
        if result["escalation_required"]:
            return "red"
        if result["post_review_required"]:
            return "red"
        return "green"

    @staticmethod
    def _explanation(result: dict[str, Any]) -> str:
        status = result["status"]
        if status == "pending":
            return "Die Notfallaktion war vorläufig wirksam. Die verpflichtende Nachprüfung durch eine zweite Person ist noch offen."
        if status == "completed_confirmed":
            return "Die Notfallaktion wurde nachträglich durch eine zweite Person bestätigt. Die ursprüngliche Notfallwirkung bleibt als historischer Vorgang erhalten."
        if status == "completed_negative":
            return "Die Nachprüfung fiel negativ aus. Die ursprüngliche Notfallwirkung wird historisch nicht umgeschrieben; stattdessen ist eine Eskalation erforderlich."
        return "Für diesen Freigabezustand besteht keine offene Notfall-Nachprüfung."
