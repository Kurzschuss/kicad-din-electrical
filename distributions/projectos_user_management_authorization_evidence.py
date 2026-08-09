"""Read-only Nachweis erfolgreicher Benutzerverwaltungs-Command-Autorisierung."""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


def _uuid(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementAuthorizationEvidence:
    """Verknüpft eine erlaubte Entscheidung mit Command-, Bus- und Audit-Nachweis."""

    command_id: str
    project_id: str
    operation: str
    actor_user_id: str
    correlation_id: str
    policy_key: str
    required_permission: str
    decision: str
    scope: str
    message_id: str | None = None
    audit_reference: str | None = None
    effective_sources: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if str(self.decision).strip() != "allow":
            raise ValueError("authorization evidence requires an allow decision")
        for name in ("operation", "policy_key", "required_permission", "scope"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must not be empty")
        object.__setattr__(self, "command_id", _uuid(self.command_id, "command_id"))
        object.__setattr__(self, "project_id", _uuid(self.project_id, "project_id"))
        object.__setattr__(self, "actor_user_id", _uuid(self.actor_user_id, "actor_user_id"))
        object.__setattr__(self, "correlation_id", _uuid(self.correlation_id, "correlation_id"))
        object.__setattr__(self, "message_id", _uuid(self.message_id, "message_id"))
        object.__setattr__(self, "operation", str(self.operation).strip())
        object.__setattr__(self, "policy_key", str(self.policy_key).strip())
        object.__setattr__(self, "required_permission", str(self.required_permission).strip())
        object.__setattr__(self, "decision", "allow")
        object.__setattr__(self, "scope", str(self.scope).strip())
        object.__setattr__(
            self,
            "effective_sources",
            tuple(MappingProxyType(dict(item)) for item in self.effective_sources),
        )
        if self.audit_reference is not None:
            object.__setattr__(self, "audit_reference", str(self.audit_reference))

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "project_id": self.project_id,
            "operation": self.operation,
            "actor_user_id": self.actor_user_id,
            "correlation_id": self.correlation_id,
            "policy_key": self.policy_key,
            "required_permission": self.required_permission,
            "decision": self.decision,
            "scope": self.scope,
            "message_id": self.message_id,
            "audit_reference": self.audit_reference,
            "effective_sources": [dict(item) for item in self.effective_sources],
            "read_only": True,
            "persisted": False,
        }
