"""Atomare Änderungsoperationen für die persistierte ProjectOS-Benutzerverwaltung.

Jede Operation erzeugt zuerst einen vollständig validierten neuen
ProjectOSUserManagementState. Erst danach wird der Managerzustand ersetzt. Der optionale
on_change-Hook ist transportneutral und für Audit-/Bus-Anbindung vorgesehen.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
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

    def _commit(
        self,
        operation: str,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
        **changes: Any,
    ) -> ProjectOSUserManagementState:
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
        self.manager._commit_user_management_change(candidate)
        event = {
            "operation": operation,
            "project_id": candidate.project_id,
            "dirty": self.manager.has_unsaved_changes,
            "read_only": False,
        }
        if command_context is not None:
            event["command_context"] = command_context.as_dict()
        if self.on_change is not None:
            self.on_change(dict(event))
        return candidate

    def _user(self, user_id: str) -> ProjectOSUserProfile:
        matches = [item for item in self.state.users if item.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("unknown user_id")
        return matches[0]

    def _role(self, role_assignment_id: str) -> ProjectOSUserProjectRole:
        matches = [item for item in self.state.project_roles if item.role_assignment_id == role_assignment_id]
        if len(matches) != 1:
            raise ValueError("unknown role_assignment_id")
        return matches[0]

    def _activation(self, activation_id: str) -> ProjectOSProjectRoleActivation:
        matches = [item for item in self.state.activations if item.activation_id == activation_id]
        if len(matches) != 1:
            raise ValueError("unknown activation_id")
        return matches[0]

    def _request(self, action_id: str) -> ProjectOSRoleActionApprovalRequest:
        matches = [item for item in self.state.approval_requests if item.action_id == action_id]
        if len(matches) != 1:
            raise ValueError("unknown action_id")
        return matches[0]

    def create_user(
        self,
        display_name: str,
        *,
        weight: int = 100,
        roles: tuple[str, ...] = (),
        user_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSUserProfile:
        kwargs: dict[str, Any] = {"display_name": display_name, "weight": weight, "roles": roles}
        if user_id is not None:
            kwargs["user_id"] = user_id
        user = ProjectOSUserProfile(**kwargs)
        self._commit("user_created", command_context=command_context, users=self.state.users + (user,))
        return user

    def change_user_weight(
        self,
        user_id: str,
        weight: int,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSUserProfile:
        matches = [user for user in self.state.users if user.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("unknown user_id")
        updated = replace(matches[0], weight=weight)
        users = tuple(updated if user.user_id == user_id else user for user in self.state.users)
        self._commit("user_weight_changed", command_context=command_context, users=users)
        return updated

    def assign_permission(
        self,
        assignment: ProjectOSPermissionAssignment,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSPermissionAssignment:
        self._commit(
            "permission_assigned",
            command_context=command_context,
            permission_assignments=self.state.permission_assignments + (assignment,),
        )
        return assignment

    def command_assign_permission(
        self,
        *,
        user_id: str,
        permission: str,
        source_type: str,
        effect: str,
        scope: str = "project",
        risk_class: str = "low",
        valid_from: str | None = None,
        valid_until: str | None = None,
        source_reference: str | None = None,
        delegated_by_user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        assignment_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSPermissionAssignment:
        self._user(user_id)
        kwargs: dict[str, Any] = {
            "user_id": user_id,
            "permission": permission,
            "source_type": source_type,
            "effect": effect,
            "scope": scope,
            "risk_class": risk_class,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "source_reference": source_reference,
            "delegated_by_user_id": delegated_by_user_id,
            "metadata": dict(metadata or {}),
        }
        if assignment_id is not None:
            kwargs["assignment_id"] = assignment_id
        return self.assign_permission(
            ProjectOSPermissionAssignment(**kwargs),
            command_context=command_context,
        )

    def assign_project_role(
        self,
        role: ProjectOSUserProjectRole,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSUserProjectRole:
        self._commit(
            "project_role_assigned",
            command_context=command_context,
            project_roles=self.state.project_roles + (role,),
        )
        return role

    def command_assign_project_role(
        self,
        *,
        user_id: str,
        role_type: str,
        scope: str = "project",
        valid_from: str | None = None,
        valid_until: str | None = None,
        assigned_by_user_id: str | None = None,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        role_assignment_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSUserProjectRole:
        self._user(user_id)
        if assigned_by_user_id is not None:
            self._user(assigned_by_user_id)
        kwargs: dict[str, Any] = {
            "project_id": self.state.project_id,
            "user_id": user_id,
            "role_type": role_type,
            "scope": scope,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "assigned_by_user_id": assigned_by_user_id,
            "source_reference": source_reference,
            "metadata": dict(metadata or {}),
        }
        if role_assignment_id is not None:
            kwargs["role_assignment_id"] = role_assignment_id
        return self.assign_project_role(
            ProjectOSUserProjectRole(**kwargs),
            command_context=command_context,
        )

    def activate_project_role(
        self,
        activation: ProjectOSProjectRoleActivation,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleActivation:
        self._commit(
            "project_role_activated",
            command_context=command_context,
            activations=self.state.activations + (activation,),
        )
        return activation

    def command_activate_project_role(
        self,
        *,
        role_assignment_id: str,
        reason: str,
        valid_from: str | None = None,
        valid_until: str | None = None,
        triggered_by_user_id: str | None = None,
        trigger_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        activation_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleActivation:
        role = self._role(role_assignment_id)
        if triggered_by_user_id is not None:
            self._user(triggered_by_user_id)
        kwargs: dict[str, Any] = {
            "project_id": self.state.project_id,
            "role_assignment_id": role.role_assignment_id,
            "user_id": role.user_id,
            "reason": reason,
            "scope": role.scope,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "triggered_by_user_id": triggered_by_user_id,
            "trigger_reference": trigger_reference,
            "metadata": dict(metadata or {}),
        }
        if activation_id is not None:
            kwargs["activation_id"] = activation_id
        return self.activate_project_role(
            ProjectOSProjectRoleActivation(**kwargs),
            command_context=command_context,
        )

    def deactivate_project_role(
        self,
        deactivation: ProjectOSProjectRoleDeactivation,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleDeactivation:
        self._commit(
            "project_role_deactivated",
            command_context=command_context,
            deactivations=self.state.deactivations + (deactivation,),
        )
        return deactivation

    def command_deactivate_project_role(
        self,
        *,
        activation_id: str,
        reason: str,
        ended_at: str,
        triggered_by_user_id: str | None = None,
        trigger_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        deactivation_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleDeactivation:
        activation = self._activation(activation_id)
        if triggered_by_user_id is not None:
            self._user(triggered_by_user_id)
        kwargs: dict[str, Any] = {
            "activation_id": activation.activation_id,
            "project_id": self.state.project_id,
            "user_id": activation.user_id,
            "reason": reason,
            "ended_at": ended_at,
            "scope": activation.scope,
            "triggered_by_user_id": triggered_by_user_id,
            "trigger_reference": trigger_reference,
            "metadata": dict(metadata or {}),
        }
        if deactivation_id is not None:
            kwargs["deactivation_id"] = deactivation_id
        return self.deactivate_project_role(
            ProjectOSProjectRoleDeactivation(**kwargs),
            command_context=command_context,
        )

    def request_approval(
        self,
        request: ProjectOSRoleActionApprovalRequest,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleActionApprovalRequest:
        self._commit(
            "approval_requested",
            command_context=command_context,
            approval_requests=self.state.approval_requests + (request,),
        )
        return request

    def command_request_approval(
        self,
        *,
        action_type: str,
        target_reference: str,
        requested_by_user_id: str,
        risk_class: str,
        requested_at: str,
        scope: str = "project",
        emergency: bool = False,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
        action_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleActionApprovalRequest:
        self._user(requested_by_user_id)
        kwargs: dict[str, Any] = {
            "project_id": self.state.project_id,
            "action_type": action_type,
            "target_reference": target_reference,
            "requested_by_user_id": requested_by_user_id,
            "risk_class": risk_class,
            "requested_at": requested_at,
            "scope": scope,
            "emergency": emergency,
            "reason": reason,
            "metadata": dict(metadata or {}),
        }
        if action_id is not None:
            kwargs["action_id"] = action_id
        return self.request_approval(
            ProjectOSRoleActionApprovalRequest(**kwargs),
            command_context=command_context,
        )

    def record_approval(
        self,
        approval: ProjectOSRoleActionApproval,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleActionApproval:
        self._commit(
            "approval_recorded",
            command_context=command_context,
            approvals=self.state.approvals + (approval,),
        )
        return approval

    def command_record_approval(
        self,
        *,
        action_id: str,
        approver_user_id: str,
        decision: str,
        decided_at: str,
        comment: str | None = None,
        approval_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleActionApproval:
        self._request(action_id)
        self._user(approver_user_id)
        kwargs: dict[str, Any] = {
            "action_id": action_id,
            "approver_user_id": approver_user_id,
            "decision": decision,
            "decided_at": decided_at,
            "comment": comment,
        }
        if approval_id is not None:
            kwargs["approval_id"] = approval_id
        return self.record_approval(
            ProjectOSRoleActionApproval(**kwargs),
            command_context=command_context,
        )

    def complete_post_review(
        self,
        review: ProjectOSRoleEmergencyPostReview,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleEmergencyPostReview:
        self._commit(
            "post_review_completed",
            command_context=command_context,
            post_reviews=self.state.post_reviews + (review,),
        )
        return review

    def command_complete_post_review(
        self,
        *,
        action_id: str,
        reviewer_user_id: str,
        result: str,
        reviewed_at: str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
        review_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSRoleEmergencyPostReview:
        self._request(action_id)
        self._user(reviewer_user_id)
        kwargs: dict[str, Any] = {
            "action_id": action_id,
            "reviewer_user_id": reviewer_user_id,
            "result": result,
            "reviewed_at": reviewed_at,
            "comment": comment,
            "metadata": dict(metadata or {}),
        }
        if review_id is not None:
            kwargs["review_id"] = review_id
        return self.complete_post_review(
            ProjectOSRoleEmergencyPostReview(**kwargs),
            command_context=command_context,
        )
