"""Autorisierte Ausführungsgrenze für ProjectOS-Benutzerverwaltungs-Commands."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_user_management_authorization_evidence import ProjectOSUserManagementAuthorizationEvidence
from .projectos_user_management_change_service import ChangeHook, ProjectOSUserManagementChangeService
from .projectos_user_management_command_authorization import ProjectOSUserManagementCommandAuthorization
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_lineage import build_permission_regrant, build_role_reassignment
from .projectos_user_management_persistence import ProjectOSUserManagementState


def _timestamp(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc)


class ProjectOSAuthorizedUserManagementChangeService(ProjectOSUserManagementChangeService):
    def __init__(self, manager, *, authorization: ProjectOSUserManagementCommandAuthorization, on_change: ChangeHook | None = None) -> None:
        if authorization.manager is not manager:
            raise ValueError("authorization is not bound to this project manager")
        super().__init__(manager, on_change=on_change)
        self.authorization = authorization
        self._last_authorization: dict[str, Any] | None = None
        self._authorization_evidence: list[ProjectOSUserManagementAuthorizationEvidence] = []
        self._authorization_runtime_generation = manager.user_management_runtime_generation

    def _sync_authorization_runtime(self) -> None:
        generation = self.manager.user_management_runtime_generation
        if generation == self._authorization_runtime_generation:
            return
        self._last_authorization = None
        self._authorization_evidence.clear()
        self._authorization_runtime_generation = generation

    @property
    def last_authorization(self) -> dict[str, Any] | None:
        self._sync_authorization_runtime()
        return dict(self._last_authorization) if self._last_authorization is not None else None

    @property
    def authorization_evidence(self) -> tuple[ProjectOSUserManagementAuthorizationEvidence, ...]:
        self._sync_authorization_runtime()
        return tuple(self._authorization_evidence)

    @property
    def latest_authorization_evidence(self) -> ProjectOSUserManagementAuthorizationEvidence | None:
        records = self.authorization_evidence
        return records[-1] if records else None

    def _trace_for_command(self, command_id: str):
        traces = getattr(self.on_change, "traces", ())
        return next((trace for trace in reversed(tuple(traces)) if trace.command_id == command_id), None)

    def _commit(
        self,
        operation: str,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
        **changes: Any,
    ) -> ProjectOSUserManagementState:
        self._sync_authorization_runtime()
        decision = self.authorization.evaluate(operation, command_context)
        self._last_authorization = dict(decision)
        if not decision["allowed"]:
            raise PermissionError(
                f"ProjectOS command authorization denied: {decision['policy_key']} ({decision['decision']})"
            )
        if command_context is None:
            raise RuntimeError("allowed authorization requires command context")
        result = super()._commit(operation, command_context=command_context, **changes)
        trace = self._trace_for_command(command_context.command_id)
        self._authorization_evidence.append(ProjectOSUserManagementAuthorizationEvidence(
            command_id=command_context.command_id,
            project_id=self.manager.project_id,
            operation=operation,
            actor_user_id=command_context.actor_user_id,
            correlation_id=command_context.correlation_id,
            policy_key=str(decision["policy_key"]),
            required_permission=str(decision["required_permission"]),
            decision="allow",
            scope=str(decision["scope"]),
            message_id=trace.message.message_id if trace is not None else None,
            audit_reference=(trace.audit_entry.get("reference") if trace is not None else None),
            effective_sources=tuple(decision.get("effective_sources", ())),
        ))
        return result

    @staticmethod
    def _actor_matches(
        command_context: ProjectOSUserManagementCommandContext | None,
        actor_user_id: str,
        field_name: str,
    ) -> None:
        if command_context is not None and command_context.actor_user_id != actor_user_id:
            raise ValueError(f"{field_name} must match command actor")

    def command_deactivate_user(
        self,
        *,
        user_id: str,
        deactivated_at: str,
        deactivated_by_user_id: str,
        reason: str,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        deactivation_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ):
        self._actor_matches(command_context, deactivated_by_user_id, "deactivated_by_user_id")
        return super().command_deactivate_user(
            user_id=user_id,
            deactivated_at=deactivated_at,
            deactivated_by_user_id=deactivated_by_user_id,
            reason=reason,
            source_reference=source_reference,
            metadata=metadata,
            deactivation_id=deactivation_id,
            command_context=command_context,
        )

    def command_reactivate_user(
        self,
        *,
        user_id: str,
        reactivated_at: str,
        reactivated_by_user_id: str,
        reason: str,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        reactivation_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ):
        self._actor_matches(command_context, reactivated_by_user_id, "reactivated_by_user_id")
        return super().command_reactivate_user(
            user_id=user_id,
            reactivated_at=reactivated_at,
            reactivated_by_user_id=reactivated_by_user_id,
            reason=reason,
            source_reference=source_reference,
            metadata=metadata,
            reactivation_id=reactivation_id,
            command_context=command_context,
        )

    def command_regrant_permission(
        self,
        *,
        predecessor_assignment_id: str,
        regranted_at: str,
        regranted_by_user_id: str,
        valid_until: str | None = None,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        assignment_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ):
        self._actor_matches(command_context, regranted_by_user_id, "regranted_by_user_id")
        assignment = build_permission_regrant(
            self.state,
            predecessor_assignment_id=predecessor_assignment_id,
            regranted_at=regranted_at,
            regranted_by_user_id=regranted_by_user_id,
            valid_until=valid_until,
            source_reference=source_reference,
            metadata=metadata,
            assignment_id=assignment_id,
        )
        self._commit(
            "permission_regranted",
            command_context=command_context,
            permission_assignments=self.state.permission_assignments + (assignment,),
        )
        return assignment

    def command_reassign_project_role(
        self,
        *,
        predecessor_role_assignment_id: str,
        reassigned_at: str,
        reassigned_by_user_id: str,
        valid_until: str | None = None,
        source_reference: str | None = None,
        metadata: dict[str, Any] | None = None,
        role_assignment_id: str | None = None,
        command_context: ProjectOSUserManagementCommandContext | None = None,
    ):
        self._actor_matches(command_context, reassigned_by_user_id, "reassigned_by_user_id")
        predecessor = self._role(predecessor_role_assignment_id)
        user = self._user(predecessor.user_id)
        at = _timestamp(reassigned_at, "reassigned_at")
        evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
            roles=self.state.project_roles,
            terminations=self.state.role_assignment_terminations,
            approval_requests=self.state.approval_requests,
            approvals=self.state.approvals,
            risk_class_map=self.authorization.role_risk_class_map,
        )
        effective_ids = {
            item.termination_id
            for item in evaluator.effective_terminations(
                project_id=self.state.project_id,
                user=user,
                scope=predecessor.scope,
                at=at,
            )
        }
        role = build_role_reassignment(
            self.state,
            predecessor_role_assignment_id=predecessor_role_assignment_id,
            reassigned_at=at.isoformat(),
            reassigned_by_user_id=reassigned_by_user_id,
            valid_until=valid_until,
            source_reference=source_reference,
            metadata=metadata,
            role_assignment_id=role_assignment_id,
            effective_termination_ids=effective_ids,
        )
        self._commit(
            "project_role_reassigned",
            command_context=command_context,
            project_roles=self.state.project_roles + (role,),
        )
        return role
