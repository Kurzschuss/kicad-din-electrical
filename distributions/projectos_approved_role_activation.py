"""Freigabegesteuerte Rechtewirkung aktivierter Projektfunktionen.

High/critical-Aktivierungen wirken nur mit explizit wirksamer Vier-Augen-Freigabe.
Notfallfreigaben dürfen vorläufig wirken, bleiben aber nachprüfungspflichtig.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation, ProjectOSProjectRoleActivationRegistry
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalEvaluator,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_user_project_roles import ProjectOSUserProjectRole

_ALLOWED_RISKS = {"low", "medium", "high", "critical"}


class ProjectOSApprovedRoleActivationEvaluator:
    """Verknüpft Aktivierung, Risikoklasse und Vier-Augen-Freigabe read-only."""

    def __init__(
        self,
        *,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        approval_requests: Iterable[ProjectOSRoleActionApprovalRequest] | None = None,
        approvals: Iterable[ProjectOSRoleActionApproval] | None = None,
        risk_class_map: dict[str, str] | None = None,
    ) -> None:
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.approval_requests = tuple(approval_requests or ())
        self.approvals = tuple(approvals or ())
        self.risk_class_map = {
            str(role_type): str(risk).strip().lower()
            for role_type, risk in (risk_class_map or {}).items()
        }
        invalid = {risk for risk in self.risk_class_map.values() if risk not in _ALLOWED_RISKS}
        if invalid:
            raise ValueError(f"unsupported risk_class: {sorted(invalid)[0]}")

        activation_ids = {item.activation_id for item in self.activations}
        requests_by_target: dict[str, list[ProjectOSRoleActionApprovalRequest]] = {}
        for request in self.approval_requests:
            if request.action_type != "activation":
                continue
            if request.target_reference not in activation_ids:
                raise ValueError("approval request references unknown activation_id")
            requests_by_target.setdefault(request.target_reference, []).append(request)
        if any(len(items) > 1 for items in requests_by_target.values()):
            raise ValueError("multiple approval requests for one activation are ambiguous")

    def state(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        registry = ProjectOSProjectRoleActivationRegistry(self.roles, self.activations)
        activation_state = registry.state(project_id=project_id, user=user, scope=scope, at=at)
        role_by_assignment = {
            item["role_assignment_id"]: item for item in activation_state["activated_roles"]
        }
        request_by_activation = {
            request.target_reference: request
            for request in self.approval_requests
            if request.action_type == "activation"
            and request.project_id == activation_state["project_id"]
            and request.scope == scope
        }
        approval_evaluator = ProjectOSRoleActionApprovalEvaluator(self.approvals)

        effective_activations = []
        blocked_activations = []
        pending_reviews = []

        for activation in activation_state["active_activations"]:
            role = role_by_assignment[activation["role_assignment_id"]]
            risk_class = self.risk_class_map.get(role["role_type"], "low")
            request = request_by_activation.get(activation["activation_id"])

            if risk_class in {"high", "critical"} and request is None:
                approval_state = {
                    "status": "approval_missing",
                    "effective": False,
                    "approval_required": True,
                    "second_person_required": True,
                    "post_review_required": False,
                    "read_only": True,
                }
            elif request is None:
                approval_state = {
                    "status": "approved_not_required",
                    "effective": True,
                    "approval_required": False,
                    "second_person_required": False,
                    "post_review_required": False,
                    "read_only": True,
                }
            else:
                if request.risk_class != risk_class:
                    raise ValueError("approval request risk_class does not match activated role risk")
                approval_state = approval_evaluator.evaluate(request)

            entry = {
                "activation": dict(activation),
                "role": dict(role),
                "risk_class": risk_class,
                "approval": approval_state,
            }
            if approval_state["effective"]:
                effective_activations.append(entry)
                if approval_state.get("post_review_required"):
                    pending_reviews.append(entry)
            else:
                blocked_activations.append(entry)

        return {
            "project_id": activation_state["project_id"],
            "user": user.as_dict(),
            "scope": scope,
            "effective_activations": effective_activations,
            "blocked_activations": blocked_activations,
            "pending_post_reviews": pending_reviews,
            "assigned_not_activated_roles": activation_state["assigned_not_activated_roles"],
            "read_only": True,
        }

    def permission_assignments(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        permission_map: dict[str, Iterable[str]],
        scope: str = "project",
        at: datetime | None = None,
    ) -> tuple[ProjectOSPermissionAssignment, ...]:
        state = self.state(project_id=project_id, user=user, scope=scope, at=at)
        assignments: list[ProjectOSPermissionAssignment] = []
        for item in state["effective_activations"]:
            role = item["role"]
            activation = item["activation"]
            approval = item["approval"]
            for permission in permission_map.get(role["role_type"], ()):
                assignments.append(
                    ProjectOSPermissionAssignment(
                        user_id=user.user_id,
                        permission=str(permission),
                        source_type="role",
                        effect="allow",
                        scope=scope,
                        risk_class=item["risk_class"],
                        valid_from=activation["valid_from"],
                        valid_until=activation["valid_until"],
                        source_reference=(
                            f"approved_project_role:{role['role_type']}:"
                            f"{role['role_assignment_id']}:{activation['activation_id']}"
                        ),
                        metadata={
                            "project_id": state["project_id"],
                            "project_role": role["role_type"],
                            "role_assignment_id": role["role_assignment_id"],
                            "activation_id": activation["activation_id"],
                            "activation_reason": activation["reason"],
                            "approval_status": approval["status"],
                            "post_review_required": bool(approval.get("post_review_required")),
                        },
                    )
                )
        return tuple(assignments)
