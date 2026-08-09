"""Autorisierte Ausführungsgrenze für ProjectOS-Benutzerverwaltungs-Commands.

Der Basissservice bleibt als atomarer Domain-Primitive für kontrollierten Bootstrap,
Migration und Tests erhalten. Produktive Command-Ausführung kann diesen Subtyp nutzen,
der unmittelbar vor jedem Commit fail-closed autorisiert. Undo/Redo läuft über denselben
Change-Service und wird damit über dieselbe Grenze geprüft.
"""
from __future__ import annotations

from typing import Any

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

    @property
    def last_authorization(self) -> dict[str, Any] | None:
        return dict(self._last_authorization) if self._last_authorization is not None else None

    def _commit(
        self,
        operation: str,
        *,
        command_context: ProjectOSUserManagementCommandContext | None = None,
        **changes: Any,
    ) -> ProjectOSUserManagementState:
        decision = self.authorization.evaluate(operation, command_context)
        self._last_authorization = dict(decision)
        if not decision["allowed"]:
            raise PermissionError(
                "ProjectOS command authorization denied: "
                f"{decision['policy_key']} ({decision['decision']})"
            )
        return super()._commit(
            operation,
            command_context=command_context,
            **changes,
        )
