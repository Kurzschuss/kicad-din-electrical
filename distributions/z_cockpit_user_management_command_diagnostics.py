"""Read-only Command-/Autorisierungsdiagnostik der ProjectOS-Benutzerverwaltung."""
from __future__ import annotations

from typing import Any

_DECISION_LABELS = {"allow": "Erlaubt", "deny": "Durch DENY verweigert", "not_granted": "Recht nicht erteilt",
                    "user_deactivated": "Benutzer deaktiviert", "missing_command_context": "Command-Kontext fehlt",
                    "unknown_actor": "Akteur unbekannt", "policy_not_configured": "Command-Policy fehlt"}


class ZCockpitUserManagementCommandDiagnosticsView:
    def __init__(self, runtime) -> None: self.runtime = runtime

    def state(self) -> dict[str, Any]:
        runtime_state = self.runtime.state(); authorization = runtime_state["last_authorization"]
        evidence = runtime_state["latest_authorization_evidence"]; history = runtime_state["command_history"]
        latest_command = runtime_state["latest_command"]
        blocked = bool(authorization is not None and not authorization.get("allowed", False))
        decision = authorization.get("decision") if authorization is not None else None
        deny_blocked = decision == "deny"; user_deactivation_blocked = decision == "user_deactivated"
        revoked_assignment_count = authorization.get("revoked_assignment_count", 0) if authorization is not None else 0
        terminated_granting_role_count = authorization.get("terminated_granting_role_count", 0) if authorization is not None else 0
        blocked_granting_role_termination_count = authorization.get("blocked_granting_role_termination_count", 0) if authorization is not None else 0
        role_termination_configuration_required = bool(authorization.get("role_termination_configuration_required", False)) if authorization is not None else False
        traffic_light = "yellow" if blocked or role_termination_configuration_required else "green"
        return {
            "project_id": runtime_state["project_id"], "traffic_light": traffic_light,
            "attention_required": bool(blocked or role_termination_configuration_required), "last_decision": decision,
            "last_decision_label": _DECISION_LABELS.get(decision, "Noch keine Entscheidung") if decision else "Noch keine Entscheidung",
            "last_allowed": authorization.get("allowed") if authorization is not None else None,
            "policy_key": authorization.get("policy_key") if authorization is not None else None,
            "required_permission": authorization.get("required_permission") if authorization is not None else None,
            "actor_user_id": authorization.get("actor_user_id") if authorization is not None else None,
            "scope": authorization.get("scope") if authorization is not None else self.runtime.policy.scope,
            "effective_sources": list(authorization.get("effective_sources", ())) if authorization is not None else [],
            "role_derived_assignment_count": authorization.get("role_derived_assignment_count", 0) if authorization is not None else 0,
            "revoked_assignment_count": revoked_assignment_count, "revocation_blocked": bool(blocked and revoked_assignment_count > 0),
            "terminated_granting_role_count": terminated_granting_role_count,
            "role_termination_blocked": bool(blocked and terminated_granting_role_count > 0),
            "blocked_granting_role_termination_count": blocked_granting_role_termination_count,
            "role_termination_approval_pending": bool(blocked_granting_role_termination_count > 0),
            "role_termination_configuration_required": role_termination_configuration_required,
            "user_deactivation_blocked": user_deactivation_blocked,
            "user_deactivation": authorization.get("user_deactivation") if authorization is not None else None,
            "deny_precedence": True, "deny_blocked": deny_blocked, "weight_used_for_decision": False,
            "last_successful_authorization_evidence": evidence, "authorization_evidence_count": runtime_state["authorization_evidence_count"],
            "command_history": history, "latest_command": latest_command, "can_undo": bool(history["can_undo"]),
            "can_redo": bool(history["can_redo"]), "trace_count": runtime_state["trace_count"],
            "message_count": runtime_state["message_count"], "read_only": True, "persisted": False,
            "note": "Die Diagnose zeigt Runtime-Nachweise einschließlich Rechtewiderrufen, Rollenbeendigungen und Benutzer-Deaktivierungen. Sie ändert weder Domainzustand, Command-Historie noch Audit-/Bus-Daten."
        }
