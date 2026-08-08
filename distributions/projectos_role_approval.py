"""Vier-Augen-Freigabevertrag für kritische Projektfunktionsaktionen.

Der Vertrag bewertet Aktivierung und Beendigung rein lesend. Hohe und kritische
Risikoklassen benötigen eine zweite, vom Auslöser verschiedene Freigabe.
Notfallaktionen dürfen separat als vorläufig wirksam markiert werden, bleiben aber
bis zur nachträglichen Freigabe ausdrücklich review-pflichtig.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

_ALLOWED_ACTIONS = {"activation", "deactivation"}
_ALLOWED_RISKS = {"low", "medium", "high", "critical"}
_ALLOWED_DECISIONS = {"approve", "reject"}


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
class ProjectOSRoleActionApproval:
    action_id: str
    approver_user_id: str
    decision: str
    decided_at: str
    comment: str | None = None
    approval_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        decision = str(self.decision).strip().lower()
        if decision not in _ALLOWED_DECISIONS:
            raise ValueError(f"unsupported approval decision: {decision}")
        object.__setattr__(self, "action_id", _uuid(self.action_id, "action_id"))
        object.__setattr__(self, "approver_user_id", _uuid(self.approver_user_id, "approver_user_id"))
        object.__setattr__(self, "approval_id", _uuid(self.approval_id, "approval_id"))
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "decided_at", _timestamp(self.decided_at, "decided_at"))

    def as_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "action_id": self.action_id,
            "approver_user_id": self.approver_user_id,
            "decision": self.decision,
            "decided_at": self.decided_at,
            "comment": self.comment,
        }


@dataclass(frozen=True)
class ProjectOSRoleActionApprovalRequest:
    project_id: str
    action_type: str
    target_reference: str
    requested_by_user_id: str
    risk_class: str
    requested_at: str
    scope: str = "project"
    emergency: bool = False
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        action_type = str(self.action_type).strip().lower()
        risk_class = str(self.risk_class).strip().lower()
        scope = str(self.scope).strip()
        target_reference = str(self.target_reference).strip()
        if action_type not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported action_type: {action_type}")
        if risk_class not in _ALLOWED_RISKS:
            raise ValueError(f"unsupported risk_class: {risk_class}")
        if not scope:
            raise ValueError("scope must not be empty")
        if not target_reference:
            raise ValueError("target_reference must not be empty")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "requested_by_user_id", _uuid(self.requested_by_user_id, "requested_by_user_id"))
        object.__setattr__(self, "action_id", _uuid(self.action_id, "action_id"))
        object.__setattr__(self, "action_type", action_type)
        object.__setattr__(self, "risk_class", risk_class)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "target_reference", target_reference)
        object.__setattr__(self, "requested_at", _timestamp(self.requested_at, "requested_at"))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def requires_four_eyes(self) -> bool:
        return self.risk_class in {"high", "critical"}

    def as_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "project_id": self.project_id,
            "action_type": self.action_type,
            "target_reference": self.target_reference,
            "requested_by_user_id": self.requested_by_user_id,
            "risk_class": self.risk_class,
            "requested_at": self.requested_at,
            "scope": self.scope,
            "emergency": bool(self.emergency),
            "reason": self.reason,
            "requires_four_eyes": self.requires_four_eyes,
            "metadata": dict(self.metadata),
        }


class ProjectOSRoleActionApprovalEvaluator:
    """Bewertet den Freigabestatus ohne Aktion oder Freigaben zu verändern."""

    def __init__(self, approvals: Iterable[ProjectOSRoleActionApproval] | None = None) -> None:
        self.approvals = tuple(approvals or ())
        ids = [item.approval_id for item in self.approvals]
        if len(ids) != len(set(ids)):
            raise ValueError("approval_id already exists")

    def evaluate(self, request: ProjectOSRoleActionApprovalRequest) -> dict[str, Any]:
        relevant = [item for item in self.approvals if item.action_id == request.action_id]
        external = [item for item in relevant if item.approver_user_id != request.requested_by_user_id]
        rejected = [item for item in external if item.decision == "reject"]
        approved = [item for item in external if item.decision == "approve"]

        if rejected:
            status = "rejected"
            effective = False
        elif not request.requires_four_eyes:
            status = "approved_not_required"
            effective = True
        elif approved:
            status = "approved"
            effective = True
        elif request.emergency:
            status = "emergency_pending_review"
            effective = True
        else:
            status = "pending_approval"
            effective = False

        return {
            "request": request.as_dict(),
            "status": status,
            "effective": effective,
            "approval_required": request.requires_four_eyes,
            "second_person_required": request.requires_four_eyes,
            "self_approval_ignored": any(item.approver_user_id == request.requested_by_user_id for item in relevant),
            "external_approval_count": len(approved),
            "external_rejection_count": len(rejected),
            "approvals": [item.as_dict() for item in relevant],
            "post_review_required": status == "emergency_pending_review",
            "read_only": True,
        }
