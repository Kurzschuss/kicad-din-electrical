"""Explizite Aktivierung projektbezogener Benutzerfunktionen.

Zuweisung und Aktivierung sind getrennt. Eine Projektfunktion wirkt erst dann auf
Berechtigungen, wenn eine passende, aktuell gültige Aktivierung vorliegt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_user_project_roles import ProjectOSUserProjectRole, ProjectOSUserProjectRoleRegistry

_ALLOWED_REASONS = {
    "manual",
    "absence",
    "incapacity",
    "vacation",
    "emergency",
    "succession",
    "temporary_transfer",
}


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _timestamp(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSProjectRoleActivation:
    """Zeitlich und sachlich begrenzte Aktivierung einer vorhandenen Projektfunktion."""

    project_id: str
    role_assignment_id: str
    user_id: str
    reason: str
    scope: str = "project"
    valid_from: str | None = None
    valid_until: str | None = None
    triggered_by_user_id: str | None = None
    trigger_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    activation_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        reason = str(self.reason).strip().lower()
        scope = str(self.scope).strip()
        if reason not in _ALLOWED_REASONS:
            raise ValueError(f"unsupported activation reason: {reason}")
        if not scope:
            raise ValueError("scope must not be empty")
        valid_from = _timestamp(self.valid_from, "valid_from")
        valid_until = _timestamp(self.valid_until, "valid_until")
        if valid_from and valid_until and datetime.fromisoformat(valid_from) > datetime.fromisoformat(valid_until):
            raise ValueError("valid_from must not be after valid_until")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "role_assignment_id", _uuid(self.role_assignment_id, "role_assignment_id"))
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "activation_id", _uuid(self.activation_id, "activation_id"))
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        if self.triggered_by_user_id is not None:
            object.__setattr__(self, "triggered_by_user_id", _uuid(self.triggered_by_user_id, "triggered_by_user_id"))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def is_active(self, at: datetime) -> bool:
        if at.tzinfo is None:
            raise ValueError("activation evaluation time must include timezone")
        current = at.astimezone(timezone.utc)
        if self.valid_from and current < datetime.fromisoformat(self.valid_from):
            return False
        if self.valid_until and current > datetime.fromisoformat(self.valid_until):
            return False
        return True

    def as_dict(self) -> dict[str, Any]:
        return {
            "activation_id": self.activation_id,
            "project_id": self.project_id,
            "role_assignment_id": self.role_assignment_id,
            "user_id": self.user_id,
            "reason": self.reason,
            "scope": self.scope,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "triggered_by_user_id": self.triggered_by_user_id,
            "trigger_reference": self.trigger_reference,
            "metadata": dict(self.metadata),
        }


class ProjectOSProjectRoleActivationRegistry:
    """Read-only Auswertung aktivierter Projektfunktionen und ihrer Rechtewirkung."""

    def __init__(
        self,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
    ) -> None:
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        activation_ids = [item.activation_id for item in self.activations]
        if len(activation_ids) != len(set(activation_ids)):
            raise ValueError("activation_id already exists")
        role_ids = {item.role_assignment_id for item in self.roles}
        for activation in self.activations:
            if activation.role_assignment_id not in role_ids:
                raise ValueError("activation references unknown role_assignment_id")

    def state(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("activation evaluation time must include timezone")
        role_registry = ProjectOSUserProjectRoleRegistry(self.roles)
        role_state = role_registry.state(project_id=project_id, user=user, scope=scope, at=current)
        candidate_role_ids = {item["role_assignment_id"] for item in role_state["active_roles"]}
        matching = [
            item for item in self.activations
            if item.project_id == role_state["project_id"]
            and item.user_id == user.user_id
            and item.scope == scope
            and item.role_assignment_id in candidate_role_ids
        ]
        active = [item for item in matching if item.is_active(current)]
        inactive = [item for item in matching if item not in active]
        active_role_ids = {item.role_assignment_id for item in active}
        activated_roles = [
            item for item in role_state["active_roles"]
            if item["role_assignment_id"] in active_role_ids
        ]
        assigned_not_activated = [
            item for item in role_state["active_roles"]
            if item["role_assignment_id"] not in active_role_ids
        ]
        return {
            "project_id": role_state["project_id"],
            "user": user.as_dict(),
            "scope": scope,
            "evaluated_at": current.astimezone(timezone.utc).isoformat(),
            "activated_roles": activated_roles,
            "assigned_not_activated_roles": assigned_not_activated,
            "inactive_assigned_roles": role_state["inactive_roles"],
            "active_activations": [item.as_dict() for item in active],
            "inactive_activations": [item.as_dict() for item in inactive],
            "read_only": True,
        }

    def permission_assignments(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        permission_map: dict[str, Iterable[str]],
        scope: str = "project",
        at: datetime | None = None,
        risk_class: str = "low",
    ) -> tuple[ProjectOSPermissionAssignment, ...]:
        state = self.state(project_id=project_id, user=user, scope=scope, at=at)
        activation_by_role = {
            item["role_assignment_id"]: item
            for item in state["active_activations"]
        }
        assignments: list[ProjectOSPermissionAssignment] = []
        for role in state["activated_roles"]:
            activation = activation_by_role[role["role_assignment_id"]]
            for permission in permission_map.get(role["role_type"], ()):
                assignments.append(
                    ProjectOSPermissionAssignment(
                        user_id=user.user_id,
                        permission=str(permission),
                        source_type="role",
                        effect="allow",
                        scope=scope,
                        risk_class=risk_class,
                        valid_from=activation["valid_from"],
                        valid_until=activation["valid_until"],
                        source_reference=(
                            f"activated_project_role:{role['role_type']}:"
                            f"{role['role_assignment_id']}:{activation['activation_id']}"
                        ),
                        metadata={
                            "project_id": state["project_id"],
                            "project_role": role["role_type"],
                            "role_assignment_id": role["role_assignment_id"],
                            "activation_id": activation["activation_id"],
                            "activation_reason": activation["reason"],
                            "triggered_by_user_id": activation["triggered_by_user_id"],
                            "trigger_reference": activation["trigger_reference"],
                        },
                    )
                )
        return tuple(assignments)
