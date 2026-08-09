"""Projektbezogene Benutzerfunktionen mit expliziter Herkunft, Gültigkeit und Scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination

_ALLOWED_PROJECT_ROLES = {"project_lead", "deputy", "trusted_person", "successor"}


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
class ProjectOSUserProjectRole:
    """Explizite Benutzerfunktion innerhalb eines Projekt-/Teilbereichs."""

    project_id: str
    user_id: str
    role_type: str
    scope: str = "project"
    valid_from: str | None = None
    valid_until: str | None = None
    assigned_by_user_id: str | None = None
    source_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    role_assignment_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        role_type = str(self.role_type).strip().lower()
        scope = str(self.scope).strip()
        if role_type not in _ALLOWED_PROJECT_ROLES:
            raise ValueError(f"unsupported project role: {role_type}")
        if not scope:
            raise ValueError("scope must not be empty")
        valid_from = _timestamp(self.valid_from, "valid_from")
        valid_until = _timestamp(self.valid_until, "valid_until")
        if valid_from and valid_until and datetime.fromisoformat(valid_from) > datetime.fromisoformat(valid_until):
            raise ValueError("valid_from must not be after valid_until")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "role_assignment_id", _uuid(self.role_assignment_id, "role_assignment_id"))
        object.__setattr__(self, "role_type", role_type)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        if self.assigned_by_user_id is not None:
            object.__setattr__(self, "assigned_by_user_id", _uuid(self.assigned_by_user_id, "assigned_by_user_id"))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def is_active(self, at: datetime) -> bool:
        if at.tzinfo is None:
            raise ValueError("role evaluation time must include timezone")
        current = at.astimezone(timezone.utc)
        if self.valid_from and current < datetime.fromisoformat(self.valid_from):
            return False
        if self.valid_until and current > datetime.fromisoformat(self.valid_until):
            return False
        return True

    def as_dict(self) -> dict[str, Any]:
        return {
            "role_assignment_id": self.role_assignment_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role_type": self.role_type,
            "scope": self.scope,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "assigned_by_user_id": self.assigned_by_user_id,
            "source_reference": self.source_reference,
            "metadata": dict(self.metadata),
        }


class ProjectOSUserProjectRoleRegistry:
    """Read-only auswertbare Sammlung projektbezogener Benutzerfunktionen."""

    def __init__(
        self,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
    ) -> None:
        self._roles = tuple(roles or ())
        self._terminations = tuple(terminations or ())
        ids = [item.role_assignment_id for item in self._roles]
        if len(ids) != len(set(ids)):
            raise ValueError("role_assignment_id already exists")
        termination_ids = [item.termination_id for item in self._terminations]
        if len(termination_ids) != len(set(termination_ids)):
            raise ValueError("termination_id already exists")
        role_ids = set(ids)
        terminated_role_ids: set[str] = set()
        for item in self._terminations:
            if item.role_assignment_id not in role_ids:
                raise ValueError("role assignment termination references unknown role_assignment_id")
            if item.role_assignment_id in terminated_role_ids:
                raise ValueError("role assignment already terminated")
            terminated_role_ids.add(item.role_assignment_id)

    def state(
        self,
        *,
        project_id: str,
        user: ProjectOSUserProfile,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        project = _uuid(project_id, "project_id")
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("role evaluation time must include timezone")
        candidates = [item for item in self._roles if item.project_id == project and item.user_id == user.user_id and item.scope == scope]
        effective_terminations = {
            item.role_assignment_id: item
            for item in self._terminations
            if item.project_id == project and item.user_id == user.user_id and item.scope == scope and item.is_effective(current)
        }
        terminated = [item for item in candidates if item.role_assignment_id in effective_terminations]
        active = [item for item in candidates if item.is_active(current) and item.role_assignment_id not in effective_terminations]
        inactive = [item for item in candidates if item not in active and item not in terminated]
        return {
            "project_id": project,
            "user": user.as_dict(),
            "scope": scope,
            "evaluated_at": current.astimezone(timezone.utc).isoformat(),
            "active_roles": [item.as_dict() for item in active],
            "inactive_roles": [item.as_dict() for item in inactive],
            "terminated_roles": [
                {"role": item.as_dict(), "termination": effective_terminations[item.role_assignment_id].as_dict()}
                for item in terminated
            ],
            "termination_count": len(terminated),
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
        assignments: list[ProjectOSPermissionAssignment] = []
        for role in state["active_roles"]:
            for permission in permission_map.get(role["role_type"], ()):
                assignments.append(ProjectOSPermissionAssignment(
                    user_id=user.user_id,
                    permission=str(permission),
                    source_type="role",
                    effect="allow",
                    scope=scope,
                    risk_class=risk_class,
                    valid_from=role["valid_from"],
                    valid_until=role["valid_until"],
                    source_reference=f"project_role:{role['role_type']}:{role['role_assignment_id']}",
                    metadata={
                        "project_id": state["project_id"],
                        "project_role": role["role_type"],
                        "role_assignment_id": role["role_assignment_id"],
                        "assigned_by_user_id": role["assigned_by_user_id"],
                    },
                ))
        return tuple(assignments)
