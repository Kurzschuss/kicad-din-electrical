"""Read-only Z_Cockpit-Sicht für Vier-Augen- und Notfallfreigaben."""
from __future__ import annotations

from typing import Any, Iterable

from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)

_STATUS_LABELS = {
    "pending_approval": "Freigabe ausstehend",
    "approved": "Freigegeben",
    "approved_not_required": "Keine zweite Freigabe erforderlich",
    "rejected": "Abgelehnt",
    "emergency_pending_review": "Notfall vorläufig wirksam – Nachprüfung erforderlich",
}
_RISK_LABELS = {
    "low": "Niedrig",
    "medium": "Mittel",
    "high": "Hoch",
    "critical": "Kritisch",
}
_ACTION_LABELS = {
    "activation": "Aktivierung",
    "deactivation": "Beendigung / Rückgabe",
}


class ZCockpitRoleActionApprovalView:
    def __init__(self, approvals: Iterable[ProjectOSRoleActionApproval] | None = None) -> None:
        self._evaluator = ProjectOSRoleActionApprovalEvaluator(approvals)

    def state(self, request: ProjectOSRoleActionApprovalRequest) -> dict[str, Any]:
        result = self._evaluator.evaluate(request)
        return {
            **result,
            "status_label": _STATUS_LABELS[result["status"]],
            "risk_label": _RISK_LABELS[request.risk_class],
            "action_label": _ACTION_LABELS[request.action_type],
            "attention_required": result["status"] in {
                "pending_approval",
                "rejected",
                "emergency_pending_review",
            },
            "explanation": self._explanation(result),
            "read_only": True,
        }

    @staticmethod
    def _explanation(result: dict[str, Any]) -> str:
        status = result["status"]
        if status == "pending_approval":
            return "Die Aktion ist noch nicht wirksam. Eine zweite, vom Auslöser verschiedene Freigabe ist erforderlich."
        if status == "approved":
            return "Die erforderliche zweite Freigabe liegt vor."
        if status == "rejected":
            return "Mindestens eine externe Ablehnung liegt vor; die Aktion ist nicht wirksam."
        if status == "emergency_pending_review":
            return "Die Notfallaktion ist vorläufig wirksam, muss aber nachträglich durch eine zweite Person geprüft werden."
        return "Für diese Risikoklasse ist keine zweite Freigabe erforderlich."
