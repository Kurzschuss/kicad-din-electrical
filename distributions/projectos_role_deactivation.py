"""Explizite Beendigung/Rückgabe aktivierter Projektfunktionen."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation, ProjectOSProjectRoleActivationRegistry
from .projectos_role_assignment_termination import ProjectOSProjectRoleAssignmentTermination
from .projectos_user_project_roles import ProjectOSUserProjectRole

_ALLOWED_END_REASONS = {
    "manual_return", "principal_returned", "period_ended", "revoked",
    "handover_completed", "emergency_ended", "succession_completed",
}


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


def _timestamp(value: str, field_name: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone")
    return parsed.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectOSProjectRoleDeactivation:
    activation_id: str
    project_id: str
    user_id: str
    reason: str
    ended_at: str
    scope: str = "project"
    triggered_by_user_id: str | None = None
    trigger_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    deactivation_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        reason = str(self.reason).strip().lower()
        scope = str(self.scope).strip()
        if reason not in _ALLOWED_END_REASONS:
            raise ValueError(f"unsupported deactivation reason: {reason}")
        if not scope:
            raise ValueError("scope must not be empty")
        object.__setattr__(self, "activation_id", _uuid(self.activation_id, "activation_id"))
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "deactivation_id", _uuid(self.deactivation_id, "deactivation_id"))
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "ended_at", _timestamp(self.ended_at, "ended_at"))
        if self.triggered_by_user_id is not None:
            object.__setattr__(self, "triggered_by_user_id", _uuid(self.triggered_by_user_id, "triggered_by_user_id"))
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def as_dict(self) -> dict[str, Any]:
        return {
            "deactivation_id": self.deactivation_id,
            "activation_id": self.activation_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "reason": self.reason,
            "ended_at": self.ended_at,
            "scope": self.scope,
            "triggered_by_user_id": self.triggered_by_user_id,
            "trigger_reference": self.trigger_reference,
            "metadata": dict(self.metadata),
        }


class ProjectOSProjectRoleLifecycleEvaluator:
    """Bewertet Aktivierungen unter Berücksichtigung beider Beendigungsarten."""

    def __init__(
        self,
        *,
        roles: Iterable[ProjectOSUserProjectRole] | None = None,
        activations: Iterable[ProjectOSProjectRoleActivation] | None = None,
        deactivations: Iterable[ProjectOSProjectRoleDeactivation] | None = None,
        role_terminations: Iterable[ProjectOSProjectRoleAssignmentTermination] | None = None,
    ) -> None:
        self.roles = tuple(roles or ())
        self.activations = tuple(activations or ())
        self.deactivations = tuple(deactivations or ())
        self.role_terminations = tuple(role_terminations or ())
        activation_ids = {item.activation_id for item in self.activations}
        seen: set[str] = set()
        for item in self.deactivations:
            if item.activation_id not in activation_ids:
                raise ValueError("deactivation references unknown activation_id")
            if item.deactivation_id in seen:
                raise ValueError("deactivation_id already exists")
            seen.add(item.deactivation_id)

    def state(self, *, project_id: str, user: ProjectOSUserProfile, scope: str = "project", at: datetime | None = None) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("lifecycle evaluation time must include timezone")
        base = ProjectOSProjectRoleActivationRegistry(
            self.roles,
            self.activations,
            self.role_terminations,
        ).state(project_id=project_id, user=user, scope=scope, at=current)
        ended_by_activation = {
            item.activation_id: item
            for item in self.deactivations
            if item.project_id == base["project_id"]
            and item.user_id == user.user_id
            and item.scope == scope
            and datetime.fromisoformat(item.ended_at) <= current.astimezone(timezone.utc)
        }
        effective_activations = [
            item for item in base["active_activations"]
            if item["activation_id"] not in ended_by_activation
        ]
        ended_activations = [
            {"activation": item, "deactivation": ended_by_activation[item["activation_id"]].as_dict()}
            for item in base["active_activations"]
            if item["activation_id"] in ended_by_activation
        ]
        effective_role_ids = {item["role_assignment_id"] for item in effective_activations}
        effective_roles = [role for role in base["activated_roles"] if role["role_assignment_id"] in effective_role_ids]
        assigned_not_effective = list(base["assigned_not_activated_roles"])
        assigned_not_effective.extend(
            role for role in base["activated_roles"] if role["role_assignment_id"] not in effective_role_ids
        )
        return {
            "project_id": base["project_id"],
            "user": user.as_dict(),
            "scope": scope,
            "evaluated_at": current.astimezone(timezone.utc).isoformat(),
            "effective_roles": effective_roles,
            "assigned_not_effective_roles": assigned_not_effective,
            "terminated_assigned_roles": base["terminated_assigned_roles"],
            "effective_activations": effective_activations,
            "ended_activations": ended_activations,
            "inactive_activations": base["inactive_activations"],
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
        activation_by_role = {item["role_assignment_id"]: item for item in state["effective_activations"]}
        result: list[ProjectOSPermissionAssignment] = []
        for role in state["effective_roles"]:
            activation = activation_by_role[role["role_assignment_id"]]
            for permission in permission_map.get(role["role_type"], ()):
                result.append(ProjectOSPermissionAssignment(
                    user_id=user.user_id,
                    permission=str(permission),
                    source_type="role",
                    effect="allow",
                    scope=scope,
                    risk_class=risk_class,
                    valid_from=activation["valid_from"],
                    valid_until=activation["valid_until"],
                    source_reference=f"effective_project_role:{role['role_type']}:{role['role_assignment_id']}:{activation['activation_id']}",
                    metadata={
                        "project_id": state["project_id"],
                        "project_role": role["role_type"],
                        "role_assignment_id": role["role_assignment_id"],
                        "activation_id": activation["activation_id"],
                        "activation_reason": activation["reason"],
                    },
                ))
        return tuple(result)
