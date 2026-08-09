"""Kompensierendes Undo/Redo für reversible ProjectOS-Benutzerverwaltungs-Commands.

Undo und Redo sind neue fachliche Änderungen. Weder Domainzustand noch Audit-Historie
werden auf einen alten Snapshot zurückgesetzt. Der erste Referenzfall ist ausschließlich
`user_weight_changed`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_history import ProjectOSUserManagementCommandRecord


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
    weight: int
    correlation_id: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "target_command_id": self.target_command_id,
            "command_id": self.command_id,
            "user_id": self.user_id,
            "weight": self.weight,
            "correlation_id": self.correlation_id,
            "snapshot_restore": False,
            "new_domain_change": True,
            "read_only_result": True,
        }


class ProjectOSUserManagementUndoRedoService:
    """Führt lineares Undo/Redo fail-closed über neue Benutzerverwaltungs-Commands aus."""

    def __init__(self, change_service: ProjectOSUserManagementChangeService) -> None:
        if change_service.command_history is None:
            raise ValueError("undo/redo requires command history")
        self.change_service = change_service
        self.history = change_service.command_history

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

    @staticmethod
    def _weight_values(record: ProjectOSUserManagementCommandRecord) -> tuple[int, int]:
        if record.operation != "user_weight_changed" or not record.reversible:
            raise ValueError("command is not a reversible user weight change")
        if set(record.before_values) != {"weight"} or set(record.after_values) != {"weight"}:
            raise ValueError("reversible user weight history is incomplete")
        return int(record.before_values["weight"]), int(record.after_values["weight"])

    def undo_latest(
        self,
        *,
        actor_user_id: str,
        correlation_id: str | None = None,
    ) -> ProjectOSUserManagementUndoRedoResult:
        target = self.history.undo_candidate()
        if target is None:
            raise ValueError("no reversible command available for undo")
        before_weight, after_weight = self._weight_values(target)
        if self._user_weight(target.reference) != after_weight:
            raise ValueError("current user weight does not match undo candidate")
        actor = self._actor(actor_user_id)
        resolved_correlation = self._correlation(target, correlation_id)
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor,
            correlation_id=resolved_correlation,
            history_action="undo",
            related_command_id=target.command_id,
        )
        updated = self.change_service.change_user_weight(
            target.reference,
            before_weight,
            command_context=context,
        )
        record = self.history.get(context.command_id)
        if record is None:
            raise RuntimeError("undo command was not recorded")
        return ProjectOSUserManagementUndoRedoResult(
            action="undo",
            target_command_id=target.command_id,
            command_id=record.command_id,
            user_id=updated.user_id,
            weight=updated.weight,
            correlation_id=record.correlation_id,
        )

    def redo_latest(
        self,
        *,
        actor_user_id: str,
        correlation_id: str | None = None,
    ) -> ProjectOSUserManagementUndoRedoResult:
        target = self.history.redo_candidate()
        if target is None:
            raise ValueError("no command available for redo")
        before_weight, after_weight = self._weight_values(target)
        if self._user_weight(target.reference) != after_weight:
            raise ValueError("current user weight does not match redo candidate")
        actor = self._actor(actor_user_id)
        resolved_correlation = self._correlation(target, correlation_id)
        context = ProjectOSUserManagementCommandContext(
            actor_user_id=actor,
            correlation_id=resolved_correlation,
            history_action="redo",
            related_command_id=target.command_id,
        )
        updated = self.change_service.change_user_weight(
            target.reference,
            before_weight,
            command_context=context,
        )
        record = self.history.get(context.command_id)
        if record is None:
            raise RuntimeError("redo command was not recorded")
        return ProjectOSUserManagementUndoRedoResult(
            action="redo",
            target_command_id=target.command_id,
            command_id=record.command_id,
            user_id=updated.user_id,
            weight=updated.weight,
            correlation_id=record.correlation_id,
        )
