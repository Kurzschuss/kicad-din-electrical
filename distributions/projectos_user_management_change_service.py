"""Atomare Änderungsoperationen für die persistierte ProjectOS-Benutzerverwaltung.

Jede Operation erzeugt zuerst einen vollständig validierten neuen
ProjectOSUserManagementState. Erst danach wird der Managerzustand ersetzt. Der optionale
on_change-Hook ist transportneutral und für spätere Audit-/Bus-Anbindung vorgesehen.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_project_roles import ProjectOSUserProjectRole

ChangeHook = Callable[[dict[str, Any]], None]


class ProjectOSUserManagementChangeService:
    """Validiert und übernimmt fachliche Benutzerverwaltungsänderungen atomar."""

    def __init__(self, manager, *, on_change: ChangeHook | None = None) -> None:
        self.manager = manager
        self.on_change = on_change

    @property
    def state(self) -> ProjectOSUserManagementState:
        return self.manager.user_management

    def _commit(self, operation: str, **changes: Any) -> ProjectOSUserManagementState:
        current = self.state
        data = {
            "project_id": current.project_id,
            "users": current.users,
            "permission_assignments": current.permission_assignments,
            "project_roles": current.project_roles,
            "activations": current.activations,
            "deactivations": current.deactivations,
            "approval_requests": current.approval_requests,
            "approvals": current.approvals,
            "post_reviews": current.post_reviews,
        }
        data.update(changes)
        candidate = ProjectOSUserManagementState(**data)
        self.manager.set_user_management(candidate)
        event = {
            "operation": operation,
            "project_id": candidate.project_id,
            "dirty": self.manager.has_unsaved_changes,
            "read_only": False,
        }
        if self.on_change is not None:
            self.on_change(dict(event))
        return candidate

    def create_user(
        self,
        display_name: str,
        *,
        weight: int = 100,
        roles: tuple[str, ...] = (),
        user_id: str | None = None,
    ) -> ProjectOSUserProfile:
        kwargs: dict[str, Any] = {"display_name": display_name, "weight": weight, "roles": roles}
        if user_id is not None:
            kwargs["user_id"] = user_id
        user = ProjectOSUserProfile(**kwargs)
        self._commit("user_created", users=self.state.users + (user,))
        return user

    def change_user_weight(self, user_id: str, weight: int) -> ProjectOSUserProfile:
        matches = [user for user in self.state.users if user.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("unknown user_id")
        updated = replace(matches[0], weight=weight)
        users = tuple(updated if user.user_id == user_id else user for user in self.state.users)
        self._commit("user_weight_changed", users=users)
        return updated

    def assign_permission(self, assignment: ProjectOSPermissionAssignment) -> ProjectOSPermissionAssignment:
        self._commit(
            "permission_assigned",
            permission_assignments=self.state.permission_assignments + (assignment,),
        )
        return assignment

    def assign_project_role(self, role: ProjectOSUserProjectRole) -> ProjectOSUserProjectRole:
        self._commit("project_role_assigned", project_roles=self.state.project_roles + (role,))
        return role

    def activate_project_role(self, activation: ProjectOSProjectRoleActivation) -> ProjectOSProjectRoleActivation:
        self._commit("project_role_activated", activations=self.state.activations + (activation,))
        return activation

    def deactivate_project_role(self, deactivation: ProjectOSProjectRoleDeactivation) -> ProjectOSProjectRoleDeactivation:
        self._commit("project_role_deactivated", deactivations=self.state.deactivations + (deactivation,))
        return deactivation

    def request_approval(self, request: ProjectOSRoleActionApprovalRequest) -> ProjectOSRoleActionApprovalRequest:
        self._commit("approval_requested", approval_requests=self.state.approval_requests + (request,))
        return request

    def record_approval(self, approval: ProjectOSRoleActionApproval) -> ProjectOSRoleActionApproval:
        self._commit("approval_recorded", approvals=self.state.approvals + (approval,))
        return approval

    def complete_post_review(self, review: ProjectOSRoleEmergencyPostReview) -> ProjectOSRoleEmergencyPostReview:
        self._commit("post_review_completed", post_reviews=self.state.post_reviews + (review,))
        return review
