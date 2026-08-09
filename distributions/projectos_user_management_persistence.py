"""Versionierter Persistenzvertrag für fachliche ProjectOS-Benutzerverwaltungsdaten.

Persistiert werden ausschließlich fachliche Eingabe-/Lifecycle-Objekte. Abgeleitete
Evaluator-Ergebnisse, Simulationen, Z_Cockpit-Sichten, Attention-Items, Breadcrumbs
und materialisierte Wissensnachweise gehören ausdrücklich nicht in diesen Vertrag.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from uuid import UUID

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_user_project_roles import ProjectOSUserProjectRole

USER_MANAGEMENT_PERSISTENCE_VERSION = 1

DERIVED_NOT_PERSISTED = (
    "authorization_evaluations",
    "simulations",
    "z_cockpit_views",
    "attention_items",
    "navigation_contexts",
    "materialized_role_knowledge",
    "approval_traces",
    "post_review_traces",
)


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementState:
    project_id: str
    users: tuple[ProjectOSUserProfile, ...] = ()
    permission_assignments: tuple[ProjectOSPermissionAssignment, ...] = ()
    project_roles: tuple[ProjectOSUserProjectRole, ...] = ()
    activations: tuple[ProjectOSProjectRoleActivation, ...] = ()
    deactivations: tuple[ProjectOSProjectRoleDeactivation, ...] = ()
    approval_requests: tuple[ProjectOSRoleActionApprovalRequest, ...] = ()
    approvals: tuple[ProjectOSRoleActionApproval, ...] = ()
    post_reviews: tuple[ProjectOSRoleEmergencyPostReview, ...] = ()

    def __post_init__(self) -> None:
        project_id = _uuid(self.project_id, "project_id")
        object.__setattr__(self, "project_id", project_id)
        self._validate_unique("user_id", self.users)
        self._validate_unique("assignment_id", self.permission_assignments)
        self._validate_unique("role_assignment_id", self.project_roles)
        self._validate_unique("activation_id", self.activations)
        self._validate_unique("deactivation_id", self.deactivations)
        self._validate_unique("action_id", self.approval_requests)
        self._validate_unique("approval_id", self.approvals)
        self._validate_unique("review_id", self.post_reviews)

        user_ids = {item.user_id for item in self.users}
        role_ids = {item.role_assignment_id for item in self.project_roles}
        activation_ids = {item.activation_id for item in self.activations}
        action_ids = {item.action_id for item in self.approval_requests}

        for item in self.project_roles:
            if item.project_id != project_id:
                raise ValueError("project role belongs to another project")
            if item.user_id not in user_ids:
                raise ValueError("project role references unknown user_id")
        for item in self.permission_assignments:
            if item.user_id not in user_ids:
                raise ValueError("permission assignment references unknown user_id")
        for item in self.activations:
            if item.project_id != project_id:
                raise ValueError("activation belongs to another project")
            if item.user_id not in user_ids:
                raise ValueError("activation references unknown user_id")
            if item.role_assignment_id not in role_ids:
                raise ValueError("activation references unknown role_assignment_id")
        for item in self.deactivations:
            if item.project_id != project_id:
                raise ValueError("deactivation belongs to another project")
            if item.user_id not in user_ids:
                raise ValueError("deactivation references unknown user_id")
            if item.activation_id not in activation_ids:
                raise ValueError("deactivation references unknown activation_id")
        for item in self.approval_requests:
            if item.project_id != project_id:
                raise ValueError("approval request belongs to another project")
            if item.requested_by_user_id not in user_ids:
                raise ValueError("approval request references unknown requested_by_user_id")
        for item in self.approvals:
            if item.action_id not in action_ids:
                raise ValueError("approval references unknown action_id")
            if item.approver_user_id not in user_ids:
                raise ValueError("approval references unknown approver_user_id")
        for item in self.post_reviews:
            if item.action_id not in action_ids:
                raise ValueError("post review references unknown action_id")
            if item.reviewer_user_id not in user_ids:
                raise ValueError("post review references unknown reviewer_user_id")

    @staticmethod
    def _validate_unique(field_name: str, items: Iterable[Any]) -> None:
        values = [getattr(item, field_name) for item in items]
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} already exists")

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": USER_MANAGEMENT_PERSISTENCE_VERSION,
            "project_id": self.project_id,
            "users": [item.as_dict() for item in self.users],
            "permission_assignments": [item.as_dict() for item in self.permission_assignments],
            "project_roles": [item.as_dict() for item in self.project_roles],
            "activations": [item.as_dict() for item in self.activations],
            "deactivations": [item.as_dict() for item in self.deactivations],
            "approval_requests": [item.as_dict() for item in self.approval_requests],
            "approvals": [item.as_dict() for item in self.approvals],
            "post_reviews": [item.as_dict() for item in self.post_reviews],
            "derived_not_persisted": list(DERIVED_NOT_PERSISTED),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectOSUserManagementState":
        if not isinstance(data, dict):
            raise ValueError("user management state must be an object")
        if data.get("version") != USER_MANAGEMENT_PERSISTENCE_VERSION:
            raise ValueError("unsupported user management persistence version")

        def rows(name: str) -> list[dict[str, Any]]:
            value = data.get(name, [])
            if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
                raise ValueError(f"{name} must be a list of objects")
            return value

        users = tuple(ProjectOSUserProfile(
            user_id=item["user_id"],
            display_name=item["display_name"],
            weight=item.get("weight", 100),
            roles=tuple(item.get("roles", ())),
        ) for item in rows("users"))
        permissions = tuple(ProjectOSPermissionAssignment(**item) for item in rows("permission_assignments"))
        project_roles = tuple(ProjectOSUserProjectRole(**item) for item in rows("project_roles"))
        activations = tuple(ProjectOSProjectRoleActivation(**item) for item in rows("activations"))
        deactivations = tuple(ProjectOSProjectRoleDeactivation(**item) for item in rows("deactivations"))
        requests = tuple(ProjectOSRoleActionApprovalRequest(
            action_id=item["action_id"], project_id=item["project_id"], action_type=item["action_type"],
            target_reference=item["target_reference"], requested_by_user_id=item["requested_by_user_id"],
            risk_class=item["risk_class"], requested_at=item["requested_at"], scope=item.get("scope", "project"),
            emergency=bool(item.get("emergency", False)), reason=item.get("reason"), metadata=dict(item.get("metadata", {})),
        ) for item in rows("approval_requests"))
        approvals = tuple(ProjectOSRoleActionApproval(**item) for item in rows("approvals"))
        reviews = tuple(ProjectOSRoleEmergencyPostReview(**item) for item in rows("post_reviews"))
        return cls(
            project_id=data["project_id"], users=users, permission_assignments=permissions,
            project_roles=project_roles, activations=activations, deactivations=deactivations,
            approval_requests=requests, approvals=approvals, post_reviews=reviews,
        )
