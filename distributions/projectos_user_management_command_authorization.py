"""Fail-closed Autorisierung für ProjectOS-Benutzerverwaltungs-Commands.

Der Autorisierer verändert keinen Fachzustand. Er bewertet den expliziten Command-Akteur
gegen persistierte Rechtezuweisungen und optional gegen Rechte aus wirksam aktivierten,
freigegebenen Projektfunktionen. Rechtewiderrufe, Benutzer-Deaktivierungen und
freigabewirksame Rollenzuweisungs-Beendigungen wirken zeitabhängig.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .projectos_approved_role_activation import ProjectOSApprovedRoleActivationEvaluator
from .projectos_authorization import ProjectOSAuthorizationEvaluator, ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_role_deactivation_approval import ProjectOSApprovedRoleDeactivationEvaluator
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext


class ProjectOSUserManagementCommandAuthorization:
    def __init__(
        self,
        manager,
        *,
        command_permission_map: Mapping[str, str],
        role_permission_map: Mapping[str, Iterable[str]] | None = None,
        role_risk_class_map: Mapping[str, str] | None = None,
        scope: str = "project",
    ) -> None:
        self.manager = manager
        self.scope = str(scope).strip()
        if not self.scope:
            raise ValueError("authorization scope must not be empty")
        self.command_permission_map = {
            str(key).strip(): str(value).strip()
            for key, value in command_permission_map.items()
            if str(key).strip() and str(value).strip()
        }
        if not self.command_permission_map:
            raise ValueError("command_permission_map must not be empty")
        self.role_permission_map = {
            str(role).strip(): tuple(dict.fromkeys(
                str(permission).strip() for permission in permissions if str(permission).strip()
            ))
            for role, permissions in (role_permission_map or {}).items()
            if str(role).strip()
        }
        self.role_risk_class_map = {
            str(role).strip(): str(risk).strip().lower()
            for role, risk in (role_risk_class_map or {}).items()
            if str(role).strip()
        }

    @staticmethod
    def policy_key(operation: str, command_context: ProjectOSUserManagementCommandContext | None) -> str:
        operation_name = str(operation).strip()
        if not operation_name:
            raise ValueError("operation must not be empty")
        if command_context is None or command_context.history_action == "command":
            return operation_name
        return f"{command_context.history_action}:{operation_name}"

    def _actor(self, actor_user_id: str) -> ProjectOSUserProfile | None:
        matches = [user for user in self.manager.user_management.users if user.user_id == actor_user_id]
        return matches[0] if len(matches) == 1 else None

    def _effective_user_deactivation(self, user_id: str, at: datetime | None):
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("authorization evaluation time must include timezone")
        matches = [
            item for item in self.manager.user_management.user_deactivations
            if item.user_id == user_id and item.is_effective(current)
        ]
        if len(matches) > 1:
            raise ValueError("multiple effective user deactivations are ambiguous")
        return matches[0] if matches else None

    @staticmethod
    def _deactivation_target(deactivation_id: str) -> str:
        return f"deactivation:{deactivation_id}"

    def _role_termination_state(self, user: ProjectOSUserProfile, *, at: datetime | None) -> dict[str, Any]:
        state = self.manager.user_management
        evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
            roles=state.project_roles,
            terminations=state.role_assignment_terminations,
            approval_requests=state.approval_requests,
            approvals=state.approvals,
            risk_class_map=self.role_risk_class_map,
        )
        return evaluator.state(project_id=state.project_id, user=user, scope=self.scope, at=at)

    def _activation_still_effective(
        self, *, user: ProjectOSUserProfile, activation_id: str,
        role_assignment_id: str, risk_class: str, at: datetime | None,
    ) -> bool:
        state = self.manager.user_management
        matching_deactivations = [
            item for item in state.deactivations
            if item.activation_id == activation_id and item.project_id == state.project_id
            and item.user_id == user.user_id and item.scope == self.scope
        ]
        if not matching_deactivations:
            return True
        if len(matching_deactivations) != 1:
            raise ValueError("multiple deactivations for one activation are ambiguous")
        deactivation = matching_deactivations[0]
        target = self._deactivation_target(deactivation.deactivation_id)
        requests = tuple(item for item in state.approval_requests if item.action_type == "deactivation" and item.target_reference == target)
        action_ids = {item.action_id for item in requests}
        approvals = tuple(item for item in state.approvals if item.action_id in action_ids)
        roles = tuple(item for item in state.project_roles if item.role_assignment_id == role_assignment_id)
        activations = tuple(item for item in state.activations if item.activation_id == activation_id)
        evaluator = ProjectOSApprovedRoleDeactivationEvaluator(
            roles=roles, activations=activations, deactivations=[deactivation], role_terminations=(),
            approval_requests=requests, approvals=approvals,
        )
        lifecycle = evaluator.state(project_id=state.project_id, user=user, scope=self.scope, at=at, risk_class=risk_class)
        return any(item["role_assignment_id"] == role_assignment_id for item in lifecycle["effective_roles"])

    def _role_assignments(self, user: ProjectOSUserProfile, *, at: datetime | None) -> tuple[ProjectOSPermissionAssignment, ...]:
        if not self.role_permission_map:
            return ()
        state = self.manager.user_management
        activation_evaluator = ProjectOSApprovedRoleActivationEvaluator(
            roles=state.project_roles, activations=state.activations,
            role_terminations=state.role_assignment_terminations,
            approval_requests=state.approval_requests, approvals=state.approvals,
            risk_class_map=self.role_risk_class_map,
        )
        candidates = activation_evaluator.permission_assignments(
            project_id=state.project_id, user=user, permission_map=self.role_permission_map,
            scope=self.scope, at=at,
        )
        effective = []
        for assignment in candidates:
            activation_id = str(assignment.metadata.get("activation_id", ""))
            role_assignment_id = str(assignment.metadata.get("role_assignment_id", ""))
            if not activation_id or not role_assignment_id:
                raise ValueError("role-derived permission lacks lifecycle references")
            if self._activation_still_effective(
                user=user, activation_id=activation_id, role_assignment_id=role_assignment_id,
                risk_class=assignment.risk_class, at=at,
            ):
                effective.append(assignment)
        return tuple(effective)

    def _granting_role_termination_diagnostics(
        self, user: ProjectOSUserProfile, required_permission: str, *, at: datetime | None,
    ) -> tuple[int, int, bool]:
        granting_role_types = {
            role_type for role_type, permissions in self.role_permission_map.items()
            if required_permission in permissions
        }
        if not granting_role_types:
            return 0, 0, False
        state = self.manager.user_management
        role_ids = {
            item.role_assignment_id for item in state.project_roles
            if item.user_id == user.user_id and item.scope == self.scope and item.role_type in granting_role_types
        }
        termination_state = self._role_termination_state(user, at=at)
        effective = sum(
            1 for item in termination_state["effective_terminations"]
            if item["role_assignment_id"] in role_ids
        )
        blocked_rows = [
            item for item in termination_state["blocked_terminations"]
            if item["termination"]["role_assignment_id"] in role_ids
        ]
        configuration_required = any(
            item["approval"].get("status") == "risk_not_configured" for item in blocked_rows
        )
        return effective, len(blocked_rows), configuration_required

    def evaluate(
        self,
        operation: str,
        command_context: ProjectOSUserManagementCommandContext | None,
        *,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        key = self.policy_key(operation, command_context)
        required_permission = self.command_permission_map.get(key)
        if command_context is None:
            return {
                "operation": str(operation).strip(), "policy_key": key, "required_permission": required_permission,
                "actor_user_id": None, "scope": self.scope, "decision": "missing_command_context", "allowed": False,
                "deny_precedence": True, "weight_used_for_decision": False, "read_only": True,
            }
        actor = self._actor(command_context.actor_user_id)
        if actor is None:
            return {
                "operation": str(operation).strip(), "policy_key": key, "required_permission": required_permission,
                "actor_user_id": command_context.actor_user_id, "scope": self.scope, "decision": "unknown_actor",
                "allowed": False, "deny_precedence": True, "weight_used_for_decision": False, "read_only": True,
            }
        if required_permission is None:
            return {
                "operation": str(operation).strip(), "policy_key": key, "required_permission": None,
                "actor_user_id": actor.user_id, "scope": self.scope, "decision": "policy_not_configured",
                "allowed": False, "deny_precedence": True, "weight_used_for_decision": False, "read_only": True,
            }

        state = self.manager.user_management
        user_deactivation = self._effective_user_deactivation(actor.user_id, at)
        if user_deactivation is not None:
            authorization = ProjectOSAuthorizationEvaluator(
                state.permission_assignments, state.permission_revocations, state.user_deactivations,
            ).evaluate(actor, required_permission, scope=self.scope, at=at)
            return {
                "operation": str(operation).strip(), "history_action": command_context.history_action,
                "related_command_id": command_context.related_command_id, "policy_key": key,
                "required_permission": required_permission, "actor_user_id": actor.user_id, "scope": self.scope,
                "decision": "user_deactivated", "allowed": False, "effective_sources": [],
                "active_assignment_count": 0, "revoked_assignment_count": authorization["revocation_count"],
                "role_derived_assignment_count": 0, "terminated_granting_role_count": 0,
                "blocked_granting_role_termination_count": 0, "role_termination_configuration_required": False,
                "user_deactivated": True, "user_deactivation": user_deactivation.as_dict(),
                "deny_precedence": True, "weight_used_for_decision": False, "read_only": True,
            }

        direct_assignments = tuple(state.permission_assignments)
        role_assignments = self._role_assignments(actor, at=at)
        authorization = ProjectOSAuthorizationEvaluator(
            direct_assignments + role_assignments, state.permission_revocations, state.user_deactivations,
        ).evaluate(actor, required_permission, scope=self.scope, at=at)
        terminated_count, blocked_termination_count, configuration_required = self._granting_role_termination_diagnostics(
            actor, required_permission, at=at,
        )
        return {
            "operation": str(operation).strip(), "history_action": command_context.history_action,
            "related_command_id": command_context.related_command_id, "policy_key": key,
            "required_permission": required_permission, "actor_user_id": actor.user_id, "scope": self.scope,
            "decision": authorization["decision"], "allowed": authorization["allowed"],
            "effective_sources": authorization["effective_sources"],
            "active_assignment_count": len(authorization["active_assignments"]),
            "revoked_assignment_count": authorization["revocation_count"],
            "role_derived_assignment_count": len(role_assignments),
            "terminated_granting_role_count": terminated_count,
            "blocked_granting_role_termination_count": blocked_termination_count,
            "role_termination_configuration_required": configuration_required,
            "user_deactivated": False, "user_deactivation": None,
            "deny_precedence": authorization["deny_precedence"],
            "weight_used_for_decision": authorization["weight_used_for_decision"], "read_only": True,
        }

    def require(
        self, operation: str, command_context: ProjectOSUserManagementCommandContext | None, *, at: datetime | None = None,
    ) -> dict[str, Any]:
        result = self.evaluate(operation, command_context, at=at)
        if not result["allowed"]:
            raise PermissionError(
                "ProjectOS command authorization denied: "
                f"{result['policy_key']} ({result['decision']})"
            )
        return result

    def __call__(self, operation: str, command_context: ProjectOSUserManagementCommandContext | None) -> dict[str, Any]:
        return self.require(operation, command_context)
