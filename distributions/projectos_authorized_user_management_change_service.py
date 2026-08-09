"""Autorisierte Ausführungsgrenze für ProjectOS-Benutzerverwaltungs-Commands.

Der Basisservice bleibt als atomarer Domain-Primitive für kontrollierten Bootstrap,
Migration und Tests erhalten. Produktive Command-Ausführung nutzt diesen Subtyp, der
unmittelbar vor jedem Commit fail-closed autorisiert. Undo/Redo läuft über denselben
Change-Service und wird damit über dieselbe Grenze geprüft.
"""
from __future__ import annotations

from typing import Any

from .projectos_user_management_authorization_evidence import (
    ProjectOSUserManagementAuthorizationEvidence,
)
from .projectos_user_management_change_service import (
    ChangeHook,
    ProjectOSUserManagementChangeService,
)
from .projectos_user_management_command_authorization import (
    ProjectOSUserManagementCommandAuthorization,
)
from .projectos_user_management_command_context import (
    ProjectOSUserManagementCommandContext,
)
from .projectos_user_management_persistence import ProjectOSUserManagementState


class ProjectOSAuthorizedUserManagementChangeService(ProjectOSUserManagementChangeService):
    """Autorisierter Change-Service mit unveränderter atomarer Fachlogik."""

    def __init__(
        self,
        manager,
        *,
        authorization: ProjectOSUserManagementCommandAuthorization,
        on_change: ChangeHook | None = None,
    ) -> None:
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
        return next(
            (trace for trace in reversed(tuple(traces)) if trace.command_id == command_id),
            None,
        )

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
                "ProjectOS command authorization denied: "
                f"{decision['policy_key']} ({decision['decision']})"
            )
        if command_context is None:
            raise RuntimeError("allowed authorization requires command context")

        result = super()._commit(
            operation,
            command_context=command_context,
            **changes,
        )
        trace = self._trace_for_command(command_context.command_id)
        self._authorization_evidence.append(
            ProjectOSUserManagementAuthorizationEvidence(
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
            )
        )
        return result
