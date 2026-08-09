"""Kompensierendes Undo/Redo für reversible ProjectOS-Benutzerverwaltungs-Commands.

Undo und Redo sind neue fachliche Änderungen. Weder Domainzustand noch Audit-Historie
werden auf einen alten Snapshot zurückgesetzt. Reversibilität wird zentral fail-closed
über ProjectOSUserManagementReversibilityPolicy entschieden.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_history import ProjectOSUserManagementCommandRecord
from .projectos_user_management_reversibility import ProjectOSUserManagementReversibilityPolicy


def _uuid(value: str, field_name: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc


@dataclass(frozen=True)
class ProjectOSUserManagementUndoRedoResult:
    action: str
    target_command_id: str
    command_id: str
    user_id: str
    correlation_id: str
    operation: str
    weight: int | None = None
    assignment_id: str | None = None
    revocation_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target_command_id": self.target_command_id,
            "command_id": self.command_id,
            "user_id": self.user_id,
            "operation": self.operation,
            "weight": self.weight,
            "assignment_id": self.assignment_id,
            "revocation_id": self.revocation_id,
            "correlation_id": self.correlation_id,
            "snapshot_restore": False,
            "new_domain_change": True,
            "read_only_result": True,
        }


class ProjectOSUserManagementUndoRedoService:
    """Führt lineares Undo/Redo fail-closed über neue Benutzerverwaltungs-Commands aus."""

    def __init__(
        self,
        change_service: ProjectOSUserManagementChangeService,
        *,
        reversibility: ProjectOSUserManagementReversibilityPolicy | None = None,
    ) -> None:
        if change_service.command_history is None:
            raise ValueError("undo/redo requires command history")
        self.change_service = change_service
        self.history = change_service.command_history
        self.reversibility = reversibility or ProjectOSUserManagementReversibilityPolicy()

    def _user_weight(self, user_id: str) -> int:
        normalized = _uuid(user_id, "user_id")
        matches = [item for item in self.change_service.state.users if item.user_id == normalized]
        if len(matches) != 1:
            raise ValueError("undo/redo target user does not exist")
        return matches[0].weight

    def _actor(self, actor_user_id: str) -> str:
        normalized = _uuid(actor_user_id, "actor_user_id")
        matches = [item for item in self.change_service.state.users if item.user_id == normalized]
        if len(matches) != 1:
            raise ValueError("undo/redo actor user does not exist")
        return normalized

    @staticmethod
    def _correlation(target: ProjectOSUserManagementCommandRecord, correlation_id: str | None) -> str:
        resolved = _uuid(correlation_id or str(uuid4()), "correlation_id")
        if resolved == target.correlation_id:
            raise ValueError("undo/redo requires a new correlation_id")
        return resolved

    def _weight_values(self, record: ProjectOSUserManagementCommandRecord) -> tuple[int, int]:
        self.reversibility.require(record.operation, compensation="restore_previous_weight")
        if record.operation != "user_weight_changed" or not record.reversible:
            raise ValueError("command is not a reversible user weight change")
        if set(record.before_values) != {"weight"} or set(record.after_values) != {"weight"}:
            raise ValueError("reversible user weight history is incomplete")
        return int(record.before_values["weight"]), int(record.after_values["weight"])

    def _permission_assignment(self, assignment_id: str):
        normalized = _uuid(assignment_id, "assignment_id")
        matches = [item for item in self.change_service.state.permission_assignments if item.assignment_id == normalized]
        if len(matches) != 1:
            raise ValueError("undo/redo permission assignment does not exist")
        return matches[0]

    def _undo_weight(self, target, actor: str, correlation: str):
        before_weight, after_weight = self._weight_values(target)
        if self._user_weight(target.reference) != after_weight:
            raise ValueError("current user weight does not match undo candidate")
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor, correlation_id=correlation,
            history_action="undo", related_command_id=target.command_id,
        )
        updated = self.change_service.change_user_weight(target.reference, before_weight, command_context=context)
        return context, ProjectOSUserManagementUndoRedoResult(
            action="undo", target_command_id=target.command_id, command_id=context.command_id,
            user_id=updated.user_id, correlation_id=correlation, operation="user_weight_changed", weight=updated.weight,
        )

    def _redo_weight(self, target, actor: str, correlation: str):
        before_weight, after_weight = self._weight_values(target)
        if self._user_weight(target.reference) != after_weight:
            raise ValueError("current user weight does not match redo candidate")
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor, correlation_id=correlation,
            history_action="redo", related_command_id=target.command_id,
        )
        updated = self.change_service.change_user_weight(target.reference, before_weight, command_context=context)
        return context, ProjectOSUserManagementUndoRedoResult(
            action="redo", target_command_id=target.command_id, command_id=context.command_id,
            user_id=updated.user_id, correlation_id=correlation, operation="user_weight_changed", weight=updated.weight,
        )

    def _undo_permission_assignment(self, target, actor: str, correlation: str):
        self.reversibility.require(target.operation, compensation="revoke_assignment")
        if target.operation not in {"permission_assigned", "permission_regranted"} or not target.reversible:
            raise ValueError("command is not a reversible permission assignment")
        assignment = self._permission_assignment(target.reference)
        if any(item.assignment_id == assignment.assignment_id for item in self.change_service.state.permission_revocations):
            raise ValueError("permission assignment is already revoked")
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor, correlation_id=correlation,
            history_action="undo", related_command_id=target.command_id,
        )
        revocation = self.change_service.command_revoke_permission(
            assignment_id=assignment.assignment_id,
            revoked_at=datetime.now(timezone.utc).isoformat(),
            revoked_by_user_id=actor,
            reason="Undo einer Rechtezuweisung",
            metadata={"compensation_of_command_id": target.command_id},
            command_context=context,
        )
        return context, ProjectOSUserManagementUndoRedoResult(
            action="undo", target_command_id=target.command_id, command_id=context.command_id,
            user_id=assignment.user_id, correlation_id=correlation, operation="permission_revoked",
            assignment_id=assignment.assignment_id, revocation_id=revocation.revocation_id,
        )

    def _redo_permission_assignment(self, target, actor: str, correlation: str):
        if target.operation != "permission_revoked" or target.history_action != "undo" or not target.reversible:
            raise ValueError("command is not a redo carrier for a permission assignment")
        if set(target.before_values) != {"assignment_id"} or set(target.after_values) != {"revocation_id"}:
            raise ValueError("permission redo history is incomplete")
        predecessor = self._permission_assignment(str(target.before_values["assignment_id"]))
        regrant = getattr(self.change_service, "command_regrant_permission", None)
        if not callable(regrant):
            raise ValueError("permission redo requires secured regrant command")
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor, correlation_id=correlation,
            history_action="redo", related_command_id=target.command_id,
        )
        successor = regrant(
            predecessor_assignment_id=predecessor.assignment_id,
            regranted_at=datetime.now(timezone.utc).isoformat(),
            regranted_by_user_id=actor,
            valid_until=predecessor.valid_until,
            metadata={"compensation_of_command_id": target.command_id},
            command_context=context,
        )
        return context, ProjectOSUserManagementUndoRedoResult(
            action="redo", target_command_id=target.command_id, command_id=context.command_id,
            user_id=successor.user_id, correlation_id=correlation, operation="permission_regranted",
            assignment_id=successor.assignment_id,
        )

    def undo_latest(
        self,
        *,
        actor_user_id: str,
        correlation_id: str | None = None,
    ) -> ProjectOSUserManagementUndoRedoResult:
        target = self.history.undo_candidate()
        if target is None:
            raise ValueError("no reversible command available for undo")
        actor = self._actor(actor_user_id)
        resolved_correlation = self._correlation(target, correlation_id)
        if target.operation == "user_weight_changed":
            context, result = self._undo_weight(target, actor, resolved_correlation)
        elif target.operation in {"permission_assigned", "permission_regranted"}:
            context, result = self._undo_permission_assignment(target, actor, resolved_correlation)
        else:
            raise ValueError("undo operation is not implemented for this reversible command")
        if self.history.get(context.command_id) is None:
            raise RuntimeError("undo command was not recorded")
        return result

    def redo_latest(
        self,
        *,
        actor_user_id: str,
        correlation_id: str | None = None,
    ) -> ProjectOSUserManagementUndoRedoResult:
        target = self.history.redo_candidate()
        if target is None:
            raise ValueError("no command available for redo")
        actor = self._actor(actor_user_id)
        resolved_correlation = self._correlation(target, correlation_id)
        if target.operation == "user_weight_changed":
            context, result = self._redo_weight(target, actor, resolved_correlation)
        elif target.operation == "permission_revoked":
            context, result = self._redo_permission_assignment(target, actor, resolved_correlation)
        else:
            raise ValueError("redo operation is not implemented for this command")
        if self.history.get(context.command_id) is None:
            raise RuntimeError("redo command was not recorded")
        return result
