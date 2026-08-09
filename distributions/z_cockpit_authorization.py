"""Read-only Rechteherkunft und Rechte-Simulation für Z_Cockpit."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .projectos_authorization import (
    ProjectOSAuthorizationEvaluator,
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)
from .projectos_permission_revocation import ProjectOSPermissionRevocation

_SOURCE_LABELS = {
    "role": "Rolle",
    "direct": "Direkte Zuweisung",
    "delegation": "Delegation",
    "deny": "DENY",
    "exception": "Ausnahme",
    "whitelist": "Whitelist",
    "blacklist": "Blacklist",
}
_EFFECT_LABELS = {"allow": "Erlaubt", "deny": "Verweigert"}
_RISK_LABELS = {
    "low": "Niedrig",
    "medium": "Mittel",
    "high": "Hoch",
    "critical": "Kritisch",
}
_DECISION_LABELS = {
    "allow": "Erlaubt",
    "deny": "Verweigert",
    "not_granted": "Nicht erteilt",
}


class ZCockpitAuthorizationView:
    """Bereitet effektive Rechte und deren Herkunft rein lesend für Z_Cockpit auf."""

    def __init__(
        self,
        user: ProjectOSUserProfile,
        assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        revocations: Iterable[ProjectOSPermissionRevocation] | None = None,
    ) -> None:
        self.user = user
        self._assignments = tuple(assignments or ())
        self._revocations = tuple(revocations or ())
        self._evaluator = ProjectOSAuthorizationEvaluator(self._assignments, self._revocations)

    def state(
        self,
        permission: str,
        *,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        result = self._evaluator.evaluate(self.user, permission, scope=scope, at=at)
        return self._decorate(result)

    def simulate(
        self,
        permission: str,
        *,
        scope: str = "project",
        hypothetical_assignments: Iterable[ProjectOSPermissionAssignment] | None = None,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        result = self._evaluator.simulate(
            self.user,
            permission,
            scope=scope,
            hypothetical_assignments=hypothetical_assignments,
            at=at,
        )
        baseline = self._decorate(result["baseline"])
        simulated = self._decorate(result["simulated"])
        return {
            "user": self.user.as_dict(),
            "permission": permission,
            "scope": scope,
            "baseline": baseline,
            "simulated": simulated,
            "decision_changed": result["decision_changed"],
            "impact": self._impact(baseline, simulated),
            "read_only": True,
            "note": (
                "Die Rechte-Simulation verändert keine gespeicherten Benutzer-, Rollen-, Rechtezuweisungs- "
                "oder Widerrufsdaten. Benutzergewichtung wird angezeigt, beeinflusst die Entscheidung aber nicht."
            ),
        }

    def _decorate(self, result: dict[str, Any]) -> dict[str, Any]:
        active = [self._source(item, active=True) for item in result["active_assignments"]]
        inactive = [self._source(item, active=False) for item in result["inactive_assignments"]]
        effective_ids = {item["assignment_id"] for item in result["effective_sources"]}
        for item in active:
            item["effective"] = item["assignment_id"] in effective_ids
        revoked = [
            {
                "assignment": self._source(item["assignment"], active=False),
                "revocation": dict(item["revocation"]),
            }
            for item in result.get("revoked_assignments", ())
        ]

        return {
            "user": result["user"],
            "permission": result["permission"],
            "scope": result["scope"],
            "evaluated_at": result["evaluated_at"],
            "decision": result["decision"],
            "decision_label": _DECISION_LABELS[result["decision"]],
            "allowed": result["allowed"],
            "sources": active,
            "inactive_sources": inactive,
            "revoked_sources": revoked,
            "revoked_source_count": len(revoked),
            "effective_source_count": len(effective_ids),
            "active_source_count": len(active),
            "inactive_source_count": len(inactive),
            "deny_precedence": result["deny_precedence"],
            "weight": result["user"]["weight"],
            "weight_used_for_decision": result["weight_used_for_decision"],
            "explanation": self._explanation(result, active),
            "read_only": True,
        }

    @staticmethod
    def _source(item: dict[str, Any], *, active: bool) -> dict[str, Any]:
        source = dict(item)
        source.update({
            "source_label": _SOURCE_LABELS[item["source_type"]],
            "effect_label": _EFFECT_LABELS[item["effect"]],
            "risk_label": _RISK_LABELS[item["risk_class"]],
            "active": active,
            "effective": False,
        })
        return source

    @staticmethod
    def _explanation(result: dict[str, Any], active: list[dict[str, Any]]) -> str:
        if result["decision"] == "not_granted":
            if result.get("revocation_count", 0):
                return "Das Recht ist nicht wirksam; mindestens eine passende Rechtezuweisung wurde fachlich widerrufen."
            if result["inactive_assignments"]:
                return "Das Recht ist derzeit nicht wirksam; vorhandene Zuweisungen sind außerhalb ihres Gültigkeitszeitraums."
            return "Für dieses Recht und diesen Gültigkeitsbereich liegt keine wirksame Zuweisung vor."
        effective = [item for item in active if item["effective"]]
        labels = ", ".join(item["source_label"] for item in effective)
        if result["decision"] == "deny":
            return f"Das Recht ist verweigert. Wirksame DENY-Herkunft: {labels}. DENY hat Vorrang vor ALLOW."
        return f"Das Recht ist erlaubt. Wirksame Herkunft: {labels}."

    @staticmethod
    def _impact(baseline: dict[str, Any], simulated: dict[str, Any]) -> dict[str, Any]:
        return {
            "before": baseline["decision"],
            "after": simulated["decision"],
            "before_label": baseline["decision_label"],
            "after_label": simulated["decision_label"],
            "became_allowed": not baseline["allowed"] and simulated["allowed"],
            "became_denied": baseline["allowed"] and not simulated["allowed"],
            "effective_source_delta": simulated["effective_source_count"] - baseline["effective_source_count"],
        }
