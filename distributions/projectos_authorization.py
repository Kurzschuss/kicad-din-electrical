"""Konservativer read-only Autorisierungsvertrag für ProjectOS.

Die Benutzergewichtung ist sichtbar und validiert, beeinflusst aber noch keine
Rechteentscheidung. Explizite DENY-Regeln haben Vorrang vor ALLOW-Regeln.
Rechtewiderrufe beenden die Wirksamkeit einer Zuweisung, ohne sie historisch zu löschen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from .projectos_permission_revocation import ProjectOSPermissionRevocation

_ALLOWED_SOURCES = {
    "role",
    "direct",
    "delegation",
    "deny",
    "exception",
    "whitelist",
    "blacklist",
}
_ALLOWED_EFFECTS = {"allow", "deny"}
_ALLOWED_RISK_CLASSES = {"low", "medium", "high", "critical"}


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
class ProjectOSUserProfile:
    """Benutzeridentität mit sichtbarer, noch nicht entscheidender Gewichtung."""

    display_name: str
    weight: int = 100
    user_id: str = field(default_factory=lambda: str(uuid4()))
    roles: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        name = str(self.display_name).strip()
        if not name:
            raise ValueError("display_name must not be empty")
        weight = int(self.weight)
        if not 0 <= weight <= 1000:
            raise ValueError("weight must be between 0 and 1000")
        roles = tuple(dict.fromkeys(str(role).strip() for role in self.roles if str(role).strip()))
        object.__setattr__(self, "display_name", name)
        object.__setattr__(self, "weight", weight)
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "roles", roles)

    def as_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "weight": self.weight,
            "roles": list(self.roles),
            "weight_affects_authorization": False,
        }


@dataclass(frozen=True)
class ProjectOSPermissionAssignment:
    """Explizite Herkunft einer Berechtigung oder Sperre."""

    user_id: str
    permission: str
    source_type: str
    effect: str
    scope: str = "project"
    risk_class: str = "low"
    valid_from: str | None = None
    valid_until: str | None = None
    source_reference: str | None = None
    delegated_by_user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    assignment_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        permission = str(self.permission).strip()
        source_type = str(self.source_type).strip().lower()
        effect = str(self.effect).strip().lower()
        scope = str(self.scope).strip()
        risk_class = str(self.risk_class).strip().lower()
        if not permission:
            raise ValueError("permission must not be empty")
        if source_type not in _ALLOWED_SOURCES:
            raise ValueError(f"unsupported source_type: {source_type}")
        if effect not in _ALLOWED_EFFECTS:
            raise ValueError(f"unsupported effect: {effect}")
        if not scope:
            raise ValueError("scope must not be empty")
        if risk_class not in _ALLOWED_RISK_CLASSES:
            raise ValueError(f"unsupported risk_class: {risk_class}")
        valid_from = _timestamp(self.valid_from, "valid_from")
        valid_until = _timestamp(self.valid_until, "valid_until")
        if valid_from and valid_until and datetime.fromisoformat(valid_from) > datetime.fromisoformat(valid_until):
            raise ValueError("valid_from must not be after valid_until")
        if source_type == "delegation" and not self.delegated_by_user_id:
            raise ValueError("delegation requires delegated_by_user_id")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")
        object.__setattr__(self, "user_id", _uuid(self.user_id, "user_id"))
        object.__setattr__(self, "assignment_id", _uuid(self.assignment_id, "assignment_id"))
        object.__setattr__(self, "permission", permission)
        object.__setattr__(self, "source_type", source_type)
        object.__setattr__(self, "effect", effect)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "risk_class", risk_class)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        if self.delegated_by_user_id:
            object.__setattr__(self, "delegated_by_user_id", _uuid(self.delegated_by_user_id, "delegated_by_user_id"))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def is_active(self, at: datetime) -> bool:
        current = at.astimezone(timezone.utc)
        if self.valid_from and current < datetime.fromisoformat(self.valid_from):
            return False
        if self.valid_until and current > datetime.fromisoformat(self.valid_until):
            return False
        return True

    def as_dict(self) -> dict[str, Any]:
        return {
            "assignment_id": self.assignment_id,
            "user_id": self.user_id,
            "permission": self.permission,
            "source_type": self.source_type,
            "effect": self.effect,
            "scope": self.scope,
            "risk_class": self.risk_class,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "source_reference": self.source_reference,
            "delegated_by_user_id": self.delegated_by_user_id,
            "metadata": dict(self.metadata),
        }


class ProjectOSAuthorizationEvaluator:
    """Ermittelt effektive Rechte samt Herkunft ohne den Eingabestand zu verändern."""

    def __init__(
        self,
        assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        revocations: Iterable[ProjectOSPermissionRevocation] | None = None,
    ) -> None:
        self._assignments = tuple(assignments or ())
        self._revocations = tuple(revocations or ())

    def evaluate(
        self,
        user: ProjectOSUserProfile,
        permission: str,
        *,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("authorization evaluation time must include timezone")
        candidates = [
            item for item in self._assignments
            if item.user_id == user.user_id
            and item.permission == permission
            and item.scope == scope
        ]
        revocation_by_assignment = {
            item.assignment_id: item
            for item in self._revocations
            if item.user_id == user.user_id
            and item.scope == scope
            and item.is_effective(current)
        }
        revoked = [item for item in candidates if item.assignment_id in revocation_by_assignment]
        active = [
            item for item in candidates
            if item.is_active(current) and item.assignment_id not in revocation_by_assignment
        ]
        inactive = [item for item in candidates if item not in active]
        denies = [item for item in active if item.effect == "deny"]
        allows = [item for item in active if item.effect == "allow"]
        allowed = bool(allows) and not denies
        decision = "deny" if denies else "allow" if allows else "not_granted"
        return {
            "user": user.as_dict(),
            "permission": permission,
            "scope": scope,
            "evaluated_at": current.astimezone(timezone.utc).isoformat(),
            "decision": decision,
            "allowed": allowed,
            "effective_sources": [item.as_dict() for item in (denies or allows)],
            "active_assignments": [item.as_dict() for item in active],
            "inactive_assignments": [item.as_dict() for item in inactive],
            "revoked_assignments": [
                {
                    "assignment": item.as_dict(),
                    "revocation": revocation_by_assignment[item.assignment_id].as_dict(),
                }
                for item in revoked
            ],
            "revocation_count": len(revoked),
            "deny_precedence": True,
            "weight_used_for_decision": False,
            "read_only": True,
        }

    def simulate(
        self,
        user: ProjectOSUserProfile,
        permission: str,
        *,
        scope: str = "project",
        hypothetical_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        baseline = self.evaluate(user, permission, scope=scope, at=at)
        simulated = ProjectOSAuthorizationEvaluator(
            self._assignments + tuple(hypothetical_assignments or ()),
            self._revocations,
        ).evaluate(user, permission, scope=scope, at=at)
        return {
            "baseline": baseline,
            "simulated": simulated,
            "decision_changed": baseline["decision"] != simulated["decision"],
            "read_only": True,
            "note": "Die Simulation verändert weder Benutzer noch gespeicherte Rechtezuweisungen oder Widerrufe.",
        }
