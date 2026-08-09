"""Read-only Konsistenzdiagnosen für ProjectOS-Benutzerverwaltungs-Lifecycle-Ketten."""
from __future__ import annotations

from typing import Any

from .din_editor_project_manager import DinEditorProjectManager


class ZCockpitUserManagementConsistencyView:
    """Prüft semantische Widersprüche in bereits geladenen Benutzerverwaltungsdaten."""

    def __init__(self, manager: DinEditorProjectManager) -> None:
        self.manager = manager

    def state(self) -> dict[str, Any]:
        state = self.manager.user_management
        issues: list[dict[str, Any]] = []
        users = {item.user_id: item for item in state.users}
        assignments = {item.assignment_id: item for item in state.permission_assignments}
        roles = {item.role_assignment_id: item for item in state.project_roles}
        activations = {item.activation_id: item for item in state.activations}
        requests = {item.action_id: item for item in state.approval_requests}

        def add(code: str, traffic_light: str, summary: str, affected: dict[str, Any]) -> None:
            priority = 30 if traffic_light == "red" else 20
            issues.append({
                "code": code,
                "traffic_light": traffic_light,
                "priority": priority,
                "summary": summary,
                "affected": affected,
            })

        for assignment in state.permission_assignments:
            if assignment.user_id not in users:
                add("UM_PERMISSION_UNKNOWN_USER", "red", "Eine Rechtezuweisung verweist auf einen unbekannten Benutzer.", {
                    "assignment_id": assignment.assignment_id,
                    "user_id": assignment.user_id,
                })

        revocation_count_by_assignment: dict[str, int] = {}
        for revocation in state.permission_revocations:
            assignment = assignments.get(revocation.assignment_id)
            revocation_count_by_assignment[revocation.assignment_id] = revocation_count_by_assignment.get(revocation.assignment_id, 0) + 1
            if assignment is None:
                add("UM_PERMISSION_REVOCATION_UNKNOWN_ASSIGNMENT", "red", "Ein Rechtewiderruf verweist auf eine unbekannte Rechtezuweisung.", {
                    "revocation_id": revocation.revocation_id,
                    "assignment_id": revocation.assignment_id,
                })
                continue
            if revocation.project_id != state.project_id:
                add("UM_PERMISSION_REVOCATION_FOREIGN_PROJECT", "red", "Ein Rechtewiderruf gehört zu einer anderen Projekt-ID.", {
                    "revocation_id": revocation.revocation_id,
                    "project_id": revocation.project_id,
                })
            if revocation.user_id != assignment.user_id:
                add("UM_PERMISSION_REVOCATION_USER_MISMATCH", "red", "Rechtewiderruf und Rechtezuweisung gehören zu unterschiedlichen Benutzern.", {
                    "revocation_id": revocation.revocation_id,
                    "assignment_id": assignment.assignment_id,
                    "revocation_user_id": revocation.user_id,
                    "assignment_user_id": assignment.user_id,
                })
            if revocation.scope != assignment.scope:
                add("UM_PERMISSION_REVOCATION_SCOPE_MISMATCH", "yellow", "Rechtewiderruf und Rechtezuweisung verwenden unterschiedliche Gültigkeitsbereiche.", {
                    "revocation_id": revocation.revocation_id,
                    "assignment_id": assignment.assignment_id,
                    "revocation_scope": revocation.scope,
                    "assignment_scope": assignment.scope,
                })
            if revocation.revoked_by_user_id not in users:
                add("UM_PERMISSION_REVOCATION_UNKNOWN_ACTOR", "red", "Ein Rechtewiderruf verweist auf einen unbekannten handelnden Benutzer.", {
                    "revocation_id": revocation.revocation_id,
                    "revoked_by_user_id": revocation.revoked_by_user_id,
                })

        for assignment_id, count in revocation_count_by_assignment.items():
            if count > 1:
                add("UM_PERMISSION_REVOCATION_AMBIGUOUS", "red", "Mehrere Widerrufe derselben Rechtezuweisung sind mehrdeutig.", {
                    "assignment_id": assignment_id,
                    "revocation_count": count,
                })

        for role in state.project_roles:
            if role.user_id not in users:
                add("UM_ROLE_UNKNOWN_USER", "red", "Eine Projektfunktion verweist auf einen unbekannten Benutzer.", {
                    "role_assignment_id": role.role_assignment_id,
                    "user_id": role.user_id,
                })
            if role.project_id != state.project_id:
                add("UM_ROLE_FOREIGN_PROJECT", "red", "Eine Projektfunktion gehört zu einer anderen Projekt-ID.", {
                    "role_assignment_id": role.role_assignment_id,
                    "project_id": role.project_id,
                })

        for activation in state.activations:
            role = roles.get(activation.role_assignment_id)
            if role is None:
                add("UM_ACTIVATION_UNKNOWN_ROLE", "red", "Eine Aktivierung verweist auf eine unbekannte Projektfunktion.", {
                    "activation_id": activation.activation_id,
                    "role_assignment_id": activation.role_assignment_id,
                })
                continue
            if activation.user_id != role.user_id:
                add("UM_ACTIVATION_USER_MISMATCH", "red", "Aktivierung und Projektfunktion gehören zu unterschiedlichen Benutzern.", {
                    "activation_id": activation.activation_id,
                    "role_assignment_id": role.role_assignment_id,
                    "activation_user_id": activation.user_id,
                    "role_user_id": role.user_id,
                })
            if activation.scope != role.scope:
                add("UM_ACTIVATION_SCOPE_MISMATCH", "yellow", "Aktivierung und Projektfunktion verwenden unterschiedliche Gültigkeitsbereiche.", {
                    "activation_id": activation.activation_id,
                    "role_assignment_id": role.role_assignment_id,
                    "activation_scope": activation.scope,
                    "role_scope": role.scope,
                })

        for deactivation in state.deactivations:
            activation = activations.get(deactivation.activation_id)
            if activation is None:
                add("UM_DEACTIVATION_UNKNOWN_ACTIVATION", "red", "Eine Beendigung verweist auf eine unbekannte Aktivierung.", {
                    "deactivation_id": deactivation.deactivation_id,
                    "activation_id": deactivation.activation_id,
                })
                continue
            if deactivation.user_id != activation.user_id:
                add("UM_DEACTIVATION_USER_MISMATCH", "red", "Beendigung und Aktivierung gehören zu unterschiedlichen Benutzern.", {
                    "deactivation_id": deactivation.deactivation_id,
                    "activation_id": activation.activation_id,
                    "deactivation_user_id": deactivation.user_id,
                    "activation_user_id": activation.user_id,
                })
            if deactivation.scope != activation.scope:
                add("UM_DEACTIVATION_SCOPE_MISMATCH", "yellow", "Beendigung und Aktivierung verwenden unterschiedliche Gültigkeitsbereiche.", {
                    "deactivation_id": deactivation.deactivation_id,
                    "activation_id": activation.activation_id,
                    "deactivation_scope": deactivation.scope,
                    "activation_scope": activation.scope,
                })

        for approval in state.approvals:
            if approval.action_id not in requests:
                add("UM_APPROVAL_UNKNOWN_REQUEST", "red", "Eine Freigabe verweist auf eine unbekannte Anforderung.", {
                    "approval_id": approval.approval_id,
                    "action_id": approval.action_id,
                })

        review_count_by_action: dict[str, int] = {}
        for review in state.post_reviews:
            request = requests.get(review.action_id)
            if request is None:
                add("UM_POST_REVIEW_UNKNOWN_REQUEST", "red", "Eine Nachprüfung verweist auf eine unbekannte Anforderung.", {
                    "review_id": review.review_id,
                    "action_id": review.action_id,
                })
                continue
            review_count_by_action[review.action_id] = review_count_by_action.get(review.action_id, 0) + 1
            if not request.emergency:
                add("UM_POST_REVIEW_NON_EMERGENCY", "red", "Eine Notfall-Nachprüfung gehört zu einer Anforderung ohne Notfallkennzeichen.", {
                    "review_id": review.review_id,
                    "action_id": review.action_id,
                })
            if review.reviewer_user_id == request.requested_by_user_id:
                add("UM_POST_REVIEW_SELF_REVIEW", "red", "Anforderer und Nachprüfer sind identisch; Vier-Augen-Nachprüfung ist verletzt.", {
                    "review_id": review.review_id,
                    "action_id": review.action_id,
                    "user_id": review.reviewer_user_id,
                })

        for action_id, count in review_count_by_action.items():
            if count > 1:
                add("UM_POST_REVIEW_AMBIGUOUS", "red", "Mehrere Nachprüfungen für dieselbe Aktion sind mehrdeutig.", {
                    "action_id": action_id,
                    "review_count": count,
                })

        issues.sort(key=lambda item: (-item["priority"], item["code"]))
        red_count = sum(1 for item in issues if item["traffic_light"] == "red")
        yellow_count = sum(1 for item in issues if item["traffic_light"] == "yellow")
        traffic_light = "red" if red_count else "yellow" if yellow_count else "green"
        return {
            "project_id": state.project_id,
            "traffic_light": traffic_light,
            "consistent": not issues,
            "issue_count": len(issues),
            "red_count": red_count,
            "yellow_count": yellow_count,
            "issues": issues,
            "checked_chains": [
                "user->permission->revocation",
                "user->role->activation->deactivation",
                "request->approval->post_review",
            ],
            "read_only": True,
            "note": "Die Diagnose verändert keine Benutzer-, Rechtewiderrufs-, Rollen-, Freigabe- oder Persistenzdaten.",
        }
