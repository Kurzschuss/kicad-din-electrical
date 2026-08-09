"""Fail-closed Reversibilitätsmatrix für ProjectOS-Benutzerverwaltungs-Commands."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class ProjectOSUserManagementReversibilityRule:
    operation: str
    reversible: bool
    compensation: str | None
    reason: str

    def __post_init__(self) -> None:
        operation = str(self.operation).strip()
        reason = str(self.reason).strip()
        compensation = str(self.compensation).strip() if self.compensation is not None else None
        if not operation:
            raise ValueError("operation must not be empty")
        if not reason:
            raise ValueError("reversibility reason must not be empty")
        if self.reversible and not compensation:
            raise ValueError("reversible operation requires compensation")
        if not self.reversible and compensation is not None:
            raise ValueError("non-reversible operation must not define compensation")
        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "compensation", compensation)
        object.__setattr__(self, "reason", reason)

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "reversible": self.reversible,
            "compensation": self.compensation,
            "reason": self.reason,
            "read_only": True,
        }


_DEFAULT_RULES = (
    ProjectOSUserManagementReversibilityRule(
        "user_created", False, None,
        "Es existiert noch keine fachliche Benutzer-Deaktivierungs-/Löschoperation.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "user_weight_changed", True, "restore_previous_weight",
        "Der vorherige Gewichtungswert kann über denselben validierten Fachcommand wiederhergestellt werden.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "permission_assigned", False, None,
        "Eine explizite Rechteentziehungs-/Widerrufsoperation ist noch nicht modelliert.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "project_role_assigned", False, None,
        "Eine explizite Aufhebung der Rollenzuweisung ist noch nicht modelliert.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "project_role_activated", False, None,
        "Eine Deaktivierung beendet eine Aktivierung historisch und ist kein automatisches Undo derselben Tatsache.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "project_role_deactivated", False, None,
        "Eine neue Aktivierung wäre ein neuer Lifecycle-Vorgang und kein Rückschreiben der historischen Beendigung.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "approval_requested", False, None,
        "Freigabeanforderungen sind historische Vorgänge; eine Rücknahmeoperation ist noch nicht modelliert.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "approval_recorded", False, None,
        "Freigabeentscheidungen bleiben historische Tatsachen und werden nicht rückwirkend entfernt.",
    ),
    ProjectOSUserManagementReversibilityRule(
        "post_review_completed", False, None,
        "Nachprüfungen bleiben historische Tatsachen und werden nicht rückwirkend entfernt.",
    ),
)


class ProjectOSUserManagementReversibilityPolicy:
    """Zentrale read-only Entscheidung, welche Operationen kompensierbar sind."""

    def __init__(
        self,
        rules: tuple[ProjectOSUserManagementReversibilityRule, ...] = _DEFAULT_RULES,
    ) -> None:
        by_operation = {rule.operation: rule for rule in rules}
        if len(by_operation) != len(rules):
            raise ValueError("reversibility operation already configured")
        self._rules: Mapping[str, ProjectOSUserManagementReversibilityRule] = MappingProxyType(by_operation)

    def rule(self, operation: str) -> ProjectOSUserManagementReversibilityRule:
        key = str(operation).strip()
        if key not in self._rules:
            raise ValueError(f"reversibility policy not configured: {key}")
        return self._rules[key]

    def is_reversible(self, operation: str) -> bool:
        return self.rule(operation).reversible

    def require(self, operation: str, *, compensation: str | None = None) -> ProjectOSUserManagementReversibilityRule:
        rule = self.rule(operation)
        if not rule.reversible:
            raise ValueError(f"operation is not reversible: {operation}")
        if compensation is not None and rule.compensation != compensation:
            raise ValueError("reversibility compensation does not match policy")
        return rule

    def state(self) -> dict[str, Any]:
        return {
            "rules": [rule.as_dict() for rule in self._rules.values()],
            "reversible_operations": [
                rule.operation for rule in self._rules.values() if rule.reversible
            ],
            "read_only": True,
            "persisted": False,
            "fail_closed": True,
        }
