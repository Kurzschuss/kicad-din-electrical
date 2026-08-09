"""Atomare Änderungsoperationen für die persistierte ProjectOS-Benutzerverwaltung.

Jede Operation erzeugt zuerst einen vollständig validierten neuen
ProjectOSUserManagementState. Erst danach wird der Managerzustand ersetzt. Der optionale
on_change-Hook ist transportneutral und für Audit-/Bus-Anbindung vorgesehen.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable
from uuid import uuid4

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_permission_revocation import ProjectOSPermissionRevocation
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
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
        self.command_history = getattr(on_change, "command_history", None)
        self._completed_command_ids: set[str] = set()
        self._runtime_generation = manager.user_management_runtime_generation

    @property
    def state(self) -> ProjectOSUserManagementState:
        return self.manager.user_management

    def _prepare_for_change(self) -> None:
        current_generation = self.manager.user_management_runtime_generation
        if current_generation != self._runtime_generation:
            self._completed_command_ids.clear()
            self._runtime_generation = current_generation
        prepare_hook = getattr(self.on_change, "prepare_for_change", None)
        if callable(prepare_hook):
            prepare_hook()
        self.command_history = getattr(self.on_change, "command_history", None)

    def _commit(
        self,
        operation: str,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
        **changes: Any,
    ) -> ProjectOSUserManagementState:
        self._prepare_for_change()
        command_id = command_context.command_id if command_context is not None else str(uuid4())
        if command_id in self._completed_command_ids:
            raise ValueError("command_id already used")
        if self.command_history is not None and self.command_history.get(command_id) is not None:
            raise ValueError("command_id already used")

        current = self.state
        data = {
            "project_id": current.project_id,
            "users": current.users,
            "permission_assignments": current.permission_assignments,
            "permission_revocations": current.permission_revocations,
            "project_roles": current.project_roles,
            "role_assignment_terminations": current.role_assignment_terminations,
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
            "command_id": command_id,
            "operation": operation,
            "project_id": candidate.project_id,
            "dirty": self.manager.has_unsaved_changes,
            "read_only": False,
        }
        if command_context is not None:
            event["command_context"] = command_context.as_dict()
        if self.on_change is not None:
            self.on_change(dict(event))
        self._completed_command_ids.add(command_id)
        return candidate

    def _user(self, user_id: str) -> ProjectOSUserProfile:
        matches = [item for item in self.state.users if item.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("unknown user_id")
        return matches[0]

    def _permission(self, assignment_id: str) -> ProjectOSPermissionAssignment:
        matches = [item for item in self.state.permission_assignments if item.assignment_id == assignment_id]
        if len(matches) != 1:
            raise ValueError("unknown assignment_id")
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
        return self.assign_permission(ProjectOSPermissionAssignment(**kwargs), command_context=command_context)

    def revoke_permission(
        self,
        revocation: ProjectOSPermissionRevocation,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSPermissionRevocation:
        self._commit(
            "permission_revoked",
            command_context=command_context,
            permission_revocations=self.state.permission_revocations + (revocation,),
        )
        return revocation

    def command_revoke_permission(
        self,
        *,
        assignment_id: str,
        revoked_at: str,
        revoked_by_user_id: str,
        reason: str,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        revocation_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSPermissionRevocation:
        assignment = self._permission(assignment_id)
        self._user(revoked_by_user_id)
        if any(item.assignment_id == assignment.assignment_id for item in self.state.permission_revocations):
            raise ValueError("permission assignment already revoked")
        kwargs: dict[str, Any] = {
            "assignment_id": assignment.assignment_id,
            "project_id": self.state.project_id,
            "user_id": assignment.user_id,
            "scope": assignment.scope,
            "revoked_at": revoked_at,
            "revoked_by_user_id": revoked_by_user_id,
            "reason": reason,
            "source_reference": source_reference,
            "metadata": dict(metadata or {}),
        }
        if revocation_id is not None:
            kwargs["revocation_id"] = revocation_id
        return self.revoke_permission(ProjectOSPermissionRevocation(**kwargs), command_context=command_context)

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
        return self.assign_project_role(ProjectOSUserProjectRole(**kwargs), command_context=command_context)

    def terminate_project_role_assignment(
        self,
        termination: ProjectOSProjectRoleAssignmentTermination,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleAssignmentTermination:
        self._commit(
            "project_role_assignment_terminated",
            command_context=command_context,
            role_assignment_terminations=self.state.role_assignment_terminations + (termination,),
        )
        return termination

    def command_terminate_project_role_assignment(
        self,
        *,
        role_assignment_id: str,
        ended_at: str,
        ended_by_user_id: str,
        reason: str,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        termination_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ) -> ProjectOSProjectRoleAssignmentTermination:
        role = self._role(role_assignment_id)
        self._user(ended_by_user_id)
        if any(item.role_assignment_id == role.role_assignment_id for item in self.state.role_assignment_terminations):
            raise ValueError("role assignment already terminated")
        kwargs: dict[str, Any] = {
            "role_assignment_id": role.role_assignment_id,
            "project_id": self.state.project_id,
            "user_id": role.user_id,
            "scope": role.scope,
            "ended_at": ended_at,
            "ended_by_user_id": ended_by_user_id,
            "reason": reason,
            "source_reference": source_reference,
            "metadata": dict(metadata or {}),
        }
        if termination_id is not None:
            kwargs["termination_id"] = termination_id
        return self.terminate_project_role_assignment(
            ProjectOSProjectRoleAssignmentTermination(**kwargs),
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
        if any(item.role_assignment_id == role.role_assignment_id for item in self.state.role_assignment_terminations):
            raise ValueError("role assignment already terminated")
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
        return self.activate_project_role(ProjectOSProjectRoleActivation(**kwargs), command_context=command_context)

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
        return self.deactivate_project_role(ProjectOSProjectRoleDeactivation(**kwargs), command_context=command_context)

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
        return self.request_approval(ProjectOSRoleActionApprovalRequest(**kwargs), command_context=command_context)

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
        return self.record_approval(ProjectOSRoleActionApproval(**kwargs), command_context=command_context)

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
        return self.complete_post_review(ProjectOSRoleEmergencyPostReview(**kwargs), command_context=command_context)
