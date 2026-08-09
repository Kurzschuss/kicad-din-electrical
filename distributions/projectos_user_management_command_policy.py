"""Zentrale, unveränderliche Policy für ProjectOS-Benutzerverwaltungs-Commands.

Die Policy ist die einzige Default-Konfigurationsquelle für Command→Recht-Zuordnungen
sowie optionale rollenabgeleitete Rechte und Risikoklassen. Rollenrechte bleiben im
Default bewusst leer: Sie werden erst wirksam, wenn ein Projekt sie explizit konfiguriert.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping


DEFAULT_COMMAND_PERMISSION_MAP = MappingProxyType({
    "user_created": "project.user_management.user.create",
    "user_weight_changed": "project.user_management.weight.change",
    "user_deactivated": "project.user_management.user.deactivate",
    "permission_assigned": "project.user_management.permission.assign",
    "permission_revoked": "project.user_management.permission.revoke",
    "permission_regranted": "project.user_management.permission.regrant",
    "project_role_assigned": "project.user_management.role.assign",
    "project_role_assignment_terminated": "project.user_management.role.terminate",
    "project_role_reassigned": "project.user_management.role.reassign",
    "project_role_activated": "project.user_management.role.activate",
    "project_role_deactivated": "project.user_management.role.deactivate",
    "approval_requested": "project.user_management.approval.request",
    "approval_recorded": "project.user_management.approval.record",
    "post_review_completed": "project.user_management.post_review.complete",
    "undo:user_weight_changed": "project.user_management.weight.undo",
    "redo:user_weight_changed": "project.user_management.weight.redo",
    "undo:permission_revoked": "project.user_management.permission.undo_assign",
    "redo:permission_regranted": "project.user_management.permission.redo_assign",
})

DEFAULT_ROLE_PERMISSION_MAP = MappingProxyType({})
DEFAULT_ROLE_RISK_CLASS_MAP = MappingProxyType({})


@dataclass(frozen=True)
class ProjectOSUserManagementCommandPolicy:
    command_permission_map: Mapping[str, str]
    role_permission_map: Mapping[str, tuple[str, ...]]
    role_risk_class_map: Mapping[str, str]
    scope: str = "project"

    def __post_init__(self) -> None:
        scope = str(self.scope).strip()
        if not scope:
            raise ValueError("command policy scope must not be empty")
        command_map = {
            str(key).strip(): str(value).strip()
            for key, value in self.command_permission_map.items()
            if str(key).strip() and str(value).strip()
        }
        if not command_map:
            raise ValueError("command_permission_map must not be empty")
        role_map = {
            str(role).strip(): tuple(dict.fromkeys(
                str(permission).strip() for permission in permissions if str(permission).strip()
            ))
            for role, permissions in self.role_permission_map.items()
            if str(role).strip()
        }
        risk_map = {
            str(role).strip(): str(risk).strip().lower()
            for role, risk in self.role_risk_class_map.items()
            if str(role).strip() and str(risk).strip()
        }
        invalid_risks = {risk for risk in risk_map.values() if risk not in {"low", "medium", "high", "critical"}}
        if invalid_risks:
            raise ValueError(f"unsupported role risk_class: {sorted(invalid_risks)[0]}")
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "command_permission_map", MappingProxyType(command_map))
        object.__setattr__(self, "role_permission_map", MappingProxyType(role_map))
        object.__setattr__(self, "role_risk_class_map", MappingProxyType(risk_map))

    @classmethod
    def default(cls) -> "ProjectOSUserManagementCommandPolicy":
        return cls(
            command_permission_map=DEFAULT_COMMAND_PERMISSION_MAP,
            role_permission_map=DEFAULT_ROLE_PERMISSION_MAP,
            role_risk_class_map=DEFAULT_ROLE_RISK_CLASS_MAP,
        )

    @classmethod
    def configured(
        cls,
        *,
        command_permission_map: Mapping[str, str] | None = None,
        role_permission_map: Mapping[str, Iterable[str]] | None = None,
        role_risk_class_map: Mapping[str, str] | None = None,
        scope: str = "project",
    ) -> "ProjectOSUserManagementCommandPolicy":
        return cls(
            command_permission_map=command_permission_map or DEFAULT_COMMAND_PERMISSION_MAP,
            role_permission_map={role: tuple(permissions) for role, permissions in (role_permission_map or {}).items()},
            role_risk_class_map=role_risk_class_map or {},
            scope=scope,
        )

    def as_dict(self) -> dict:
        return {
            "command_permission_map": dict(self.command_permission_map),
            "role_permission_map": {role: list(permissions) for role, permissions in self.role_permission_map.items()},
            "role_risk_class_map": dict(self.role_risk_class_map),
            "scope": self.scope,
            "read_only": True,
            "persisted": False,
        }
