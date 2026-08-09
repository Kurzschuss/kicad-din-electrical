"""Read-only Offboarding-/Verantwortungsdiagnostik für ProjectOS.

Die Diagnose materialisiert ausschließlich vorhandene Lifecycle-Tatsachen. Sie führt
keine Widerrufe, Rollenbeendigungen, Freigaben, Handovers oder Closure-Schritte aus.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .projectos_role_assignment_termination_approval import (
    ProjectOSApprovedRoleAssignmentTerminationEvaluator,
)
from .projectos_user_lifecycle import ProjectOSUserLifecycleEvaluator
from .projectos_user_management_persistence import ProjectOSUserManagementState


class ProjectOSOffboardingResponsibilityDiagnostic:
    """Ermittelt noch aufzulösende Benutzerverantwortungen ohne Nebenwirkungen."""

    def __init__(
        self,
        user_management: ProjectOSUserManagementState,
        *,
        role_risk_class_map: Mapping[str, str] | None = None,
    ) -> None:
        self.user_management = user_management
        self.role_risk_class_map = {
            str(role_type).strip(): str(risk).strip().lower()
            for role_type, risk in (role_risk_class_map or {}).items()
            if str(role_type).strip()
        }

    def _user(self, user_id: str):
        matches = [item for item in self.user_management.users if item.user_id == user_id]
        if len(matches) != 1:
            raise ValueError("unknown user_id")
        return matches[0]

    def state(
        self,
        user_id: str,
        *,
        scope: str = "project",
        at: datetime | None = None,
    ) -> dict[str, Any]:
        current = at or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("offboarding diagnostic time must include timezone")
        current = current.astimezone(timezone.utc)
        user = self._user(user_id)
        state = self.user_management

        lifecycle = ProjectOSUserLifecycleEvaluator(
            deactivations=state.user_deactivations,
            reactivations=state.user_reactivations,
        ).state(user_id=user.user_id, at=current)

        effective_revocations = {
            item.assignment_id: item
            for item in state.permission_revocations
            if item.user_id == user.user_id
            and item.scope == scope
            and item.is_effective(current)
        }
        retained_permissions = [
            item
            for item in state.permission_assignments
            if item.user_id == user.user_id
            and item.scope == scope
            and item.effect == "allow"
            and item.source_type != "role"
            and item.is_active(current)
            and item.assignment_id not in effective_revocations
        ]

        termination_evaluator = ProjectOSApprovedRoleAssignmentTerminationEvaluator(
            roles=state.project_roles,
            terminations=state.role_assignment_terminations,
            approval_requests=state.approval_requests,
            approvals=state.approvals,
            risk_class_map=self.role_risk_class_map,
        )
        termination_state = termination_evaluator.state(
            project_id=state.project_id,
            user=user,
            scope=scope,
            at=current,
        )
        effective_termination_role_ids = {
            item["role_assignment_id"]
            for item in termination_state["effective_terminations"]
        }
        active_roles = [
            item
            for item in state.project_roles
            if item.project_id == state.project_id
            and item.user_id == user.user_id
            and item.scope == scope
            and item.is_active(current)
            and item.role_assignment_id not in effective_termination_role_ids
        ]
        active_role_ids = {item.role_assignment_id for item in active_roles}

        blocked_terminations = [
            item
            for item in termination_state["blocked_terminations"]
            if item["role"]["role_assignment_id"] in active_role_ids
        ]
        scheduled_terminations = [
            item
            for item in termination_state["scheduled_terminations"]
            if item["role"]["role_assignment_id"] in active_role_ids
        ]
        pending_post_reviews = list(termination_state["pending_post_reviews"])

        blocked_by_role = {
            item["role"]["role_assignment_id"]: item
            for item in blocked_terminations
        }
        scheduled_by_role = {
            item["role"]["role_assignment_id"]: item
            for item in scheduled_terminations
        }
        role_rows: list[dict[str, Any]] = []
        for role in active_roles:
            risk_class = self.role_risk_class_map.get(role.role_type)
            blocked = blocked_by_role.get(role.role_assignment_id)
            scheduled = scheduled_by_role.get(role.role_assignment_id)
            if blocked is not None:
                termination_status = blocked["approval"]["status"]
                termination = blocked["termination"]
            elif scheduled is not None:
                termination_status = "scheduled"
                termination = scheduled["termination"]
            else:
                termination_status = "not_started"
                termination = None
            role_rows.append(
                {
                    "role": role.as_dict(),
                    "risk_class": risk_class,
                    "risk_configuration_required": risk_class is None,
                    "termination_status": termination_status,
                    "termination": termination,
                }
            )

        permission_rows = [
            {
                "assignment": item.as_dict(),
                "resolution": "revoke_or_expire",
            }
            for item in retained_permissions
        ]
        attention_items: list[dict[str, Any]] = [
            {
                "type": "permission_assignment",
                "reference": item.assignment_id,
                "label": item.permission,
                "risk_class": item.risk_class,
            }
            for item in retained_permissions
        ]
        attention_items.extend(
            {
                "type": "project_role_assignment",
                "reference": item["role"]["role_assignment_id"],
                "label": item["role"]["role_type"],
                "risk_class": item["risk_class"],
                "termination_status": item["termination_status"],
            }
            for item in role_rows
        )
        attention_items.extend(
            {
                "type": "role_termination_post_review",
                "reference": item["termination"]["termination_id"],
                "label": item["role"]["role_type"],
                "risk_class": item["risk_class"],
                "termination_status": item["approval"]["status"],
            }
            for item in pending_post_reviews
        )

        resolution_required = bool(
            retained_permissions or active_roles or pending_post_reviews
        )
        return {
            "project_id": state.project_id,
            "user": user.as_dict(),
            "scope": scope,
            "evaluated_at": current.isoformat(),
            "user_lifecycle_status": lifecycle["status"],
            "user_deactivated": lifecycle["deactivated"],
            "latest_user_lifecycle_event_type": lifecycle["latest_event_type"],
            "latest_user_lifecycle_event": lifecycle["latest_event"],
            "retained_permission_assignments": permission_rows,
            "retained_permission_assignment_count": len(permission_rows),
            "active_project_roles": role_rows,
            "active_project_role_count": len(role_rows),
            "blocked_role_terminations": blocked_terminations,
            "blocked_role_termination_count": len(blocked_terminations),
            "scheduled_role_terminations": scheduled_terminations,
            "scheduled_role_termination_count": len(scheduled_terminations),
            "pending_role_termination_post_reviews": pending_post_reviews,
            "pending_role_termination_post_review_count": len(pending_post_reviews),
            "role_risk_configuration_required": any(
                item["risk_configuration_required"] for item in role_rows
            ),
            "attention_items": attention_items,
            "attention_count": len(attention_items),
            "resolution_required": resolution_required,
            "closure_evaluated": False,
            "handover_performed": False,
            "mutation_performed": False,
            "read_only": True,
            "persisted": False,
            "note": (
                "Eine Benutzer-Deaktivierung beendet bestehende Rechte- und Rollenbezüge nicht. "
                "Die Diagnose zeigt nur offene Verantwortungen; Handover und Closure sind nicht Bestandteil dieses Vertrags."
            ),
        }
