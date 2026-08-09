"""Produktive Assembly der gesicherten ProjectOS-Benutzerverwaltungs-Runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .projectos_authorized_user_management_change_service import (
    ProjectOSAuthorizedUserManagementChangeService,
)
from .projectos_user_management_change_trace import (
    ProjectOSUserManagementChangeTraceEmitter,
)
from .projectos_user_management_command_authorization import (
    ProjectOSUserManagementCommandAuthorization,
)
from .projectos_user_management_command_policy import (
    ProjectOSUserManagementCommandPolicy,
)
from .projectos_user_management_undo_redo import ProjectOSUserManagementUndoRedoService


@dataclass(frozen=True)
class ProjectOSUserManagementRuntime:
    """Gemeinsam gebundene produktive Command-, Audit- und Undo/Redo-Grenze."""

    manager: Any
    policy: ProjectOSUserManagementCommandPolicy
    emitter: ProjectOSUserManagementChangeTraceEmitter
    authorization: ProjectOSUserManagementCommandAuthorization
    changes: ProjectOSAuthorizedUserManagementChangeService
    undo_redo: ProjectOSUserManagementUndoRedoService

    def state(self) -> dict[str, Any]:
        latest = self.emitter.command_history.latest()
        return {
            "project_id": self.manager.project_id,
            "policy": self.policy.as_dict(),
            "last_authorization": self.changes.last_authorization,
            "command_history": self.emitter.command_history.state(),
            "latest_command": latest.as_dict() if latest is not None else None,
            "trace_count": len(self.emitter.traces),
            "message_count": len(self.emitter.messages),
            "read_only": True,
            "persisted": False,
        }


def build_projectos_user_management_runtime(
    manager,
    *,
    policy: ProjectOSUserManagementCommandPolicy | None = None,
    emitter: ProjectOSUserManagementChangeTraceEmitter | None = None,
) -> ProjectOSUserManagementRuntime:
    """Baut den produktiven Benutzerverwaltungs-Einstieg fail-closed zusammen."""
    resolved_policy = policy or ProjectOSUserManagementCommandPolicy.default()
    resolved_emitter = emitter or ProjectOSUserManagementChangeTraceEmitter(manager)
    if resolved_emitter.manager is not manager:
        raise ValueError("trace emitter is not bound to this project manager")

    authorization = ProjectOSUserManagementCommandAuthorization(
        manager,
        command_permission_map=resolved_policy.command_permission_map,
        role_permission_map=resolved_policy.role_permission_map,
        role_risk_class_map=resolved_policy.role_risk_class_map,
        scope=resolved_policy.scope,
    )
    changes = ProjectOSAuthorizedUserManagementChangeService(
        manager,
        authorization=authorization,
        on_change=resolved_emitter,
    )
    undo_redo = ProjectOSUserManagementUndoRedoService(changes)
    return ProjectOSUserManagementRuntime(
        manager=manager,
        policy=resolved_policy,
        emitter=resolved_emitter,
        authorization=authorization,
        changes=changes,
        undo_redo=undo_redo,
    )
