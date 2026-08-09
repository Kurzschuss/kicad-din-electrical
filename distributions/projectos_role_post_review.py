"""Explizite Nachprüfung vorläufig wirksamer Notfall-Rollenaktionen.

Eine Nachprüfung verändert die ursprüngliche Notfallentscheidung nicht rückwirkend.
Sie dokumentiert als eigener Lifecycle-Schritt, ob die vorläufige Notfallwirkung
nachträglich bestätigt wurde oder eine Eskalation erforderlich ist.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)

_ALLOWED_RESULTS = {"confirmed", "negative"}


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _timestamp(value: str, field_name: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSRoleEmergencyPostReview:
    """Nachträgliche Prüfung einer vorläufig wirksamen Notfallaktion."""

    action_id: str
    reviewer_user_id: str
    result: str
    reviewed_at: str
    comment: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    review_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        result = str(self.result).strip().lower()
        if result not in _ALLOWED_RESULTS:
            raise ValueError(f"unsupported post review result: {result}")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "action_id", _uuid(self.action_id, "action_id"))
        object.__setattr__(self, "reviewer_user_id", _uuid(self.reviewer_user_id, "reviewer_user_id"))
        object.__setattr__(self, "review_id", _uuid(self.review_id, "review_id"))
        object.__setattr__(self, "result", result)
        object.__setattr__(self, "reviewed_at", _timestamp(self.reviewed_at, "reviewed_at"))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def as_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "action_id": self.action_id,
            "reviewer_user_id": self.reviewer_user_id,
            "result": self.result,
            "reviewed_at": self.reviewed_at,
            "comment": self.comment,
            "metadata": dict(self.metadata),
        }


class ProjectOSRoleEmergencyPostReviewEvaluator:
    """Bewertet den Abschluss offener Notfall-Nachprüfungen read-only."""

    def __init__(
        self,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        reviews: Iterable[ProjectOSRoleEmergencyPostReview] | None = None,
    ) -> None:
        self.approvals = tuple(approvals or ())
        self.reviews = tuple(reviews or ())
        review_ids = [item.review_id for item in self.reviews]
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("review_id already exists")

    def evaluate(self, request: ProjectOSRoleActionApprovalRequest) -> dict[str, Any]:
        approval_state = ProjectOSRoleActionApprovalEvaluator(self.approvals).evaluate(request)
        relevant = [item for item in self.reviews if item.action_id == request.action_id]
        if len(relevant) > 1:
            raise ValueError("multiple post reviews for action_id are ambiguous")

        if approval_state["status"] != "emergency_pending_review":
            if relevant:
                raise ValueError("post review requires emergency_pending_review approval state")
            status = "not_required"
            completed = False
            escalation_required = False
            review = None
        elif not relevant:
            status = "pending"
            completed = False
            escalation_required = False
            review = None
        else:
            review = relevant[0]
            if review.reviewer_user_id == request.requested_by_user_id:
                raise ValueError("emergency post review requires a different reviewer")
            if review.result == "confirmed":
                status = "completed_confirmed"
                completed = True
                escalation_required = False
            else:
                status = "completed_negative"
                completed = True
                escalation_required = True

        return {
            "request": request.as_dict(),
            "approval_state": approval_state,
            "status": status,
            "post_review_required": approval_state["status"] == "emergency_pending_review" and not completed,
            "post_review_completed": completed,
            "escalation_required": escalation_required,
            "review": review.as_dict() if review is not None else None,
            "historical_emergency_effect_preserved": True,
            "read_only": True,
        }
