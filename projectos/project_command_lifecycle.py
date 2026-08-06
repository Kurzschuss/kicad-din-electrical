"""Vollständige Lebenszyklusansicht für ProjectOS-Commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .identifiers import BusinessId
from .project_command_admin import CommandAdministrationService, CommandRecoveryRecord
from .project_command_history import CommandExecutionRecord, CommandExecutionStatus
from .project_command_retry import CommandRetryRecord, RecoveredCommandExecutionService


class CommandLifecycleState(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    REJECTED = "REJECTED"
    READY_FOR_RETRY = "READY_FOR_RETRY"
    RETRY_REJECTED = "RETRY_REJECTED"
    SUCCEEDED = "SUCCEEDED"


@dataclass(frozen=True, slots=True)
class CommandLifecycleView:
    """Chronologische, unveränderliche Sicht auf den gesamten Command-Lebenszyklus."""

    command_id: BusinessId
    archived_executions: tuple[CommandExecutionRecord, ...]
    current_execution: CommandExecutionRecord | None
    recoveries: tuple[CommandRecoveryRecord, ...]
    retry_attempts: tuple[CommandRetryRecord, ...]
    state: CommandLifecycleState

    @property
    def original_execution(self) -> CommandExecutionRecord | None:
        if self.archived_executions:
            return self.archived_executions[0]
        return self.current_execution


class CommandLifecycleService:
    """Führt Historie, Wiederaufnahmen und Folgeversuche zu einer Sicht zusammen."""

    def __init__(
        self,
        administration: CommandAdministrationService,
        retries: RecoveredCommandExecutionService,
    ) -> None:
        self._administration = administration
        self._retries = retries

    def get(self, command_id: BusinessId) -> CommandLifecycleView:
        archived = self._administration.archived_executions(command_id)
        current = self._administration.get(command_id)
        recoveries = tuple(
            item for item in self._administration.recoveries() if item.command_id == command_id
        )
        attempts = self._retries.attempts(command_id)
        return CommandLifecycleView(
            command_id=command_id,
            archived_executions=archived,
            current_execution=current,
            recoveries=recoveries,
            retry_attempts=attempts,
            state=self._state(archived, current, recoveries, attempts),
        )

    @staticmethod
    def _state(
        archived: tuple[CommandExecutionRecord, ...],
        current: CommandExecutionRecord | None,
        recoveries: tuple[CommandRecoveryRecord, ...],
        attempts: tuple[CommandRetryRecord, ...],
    ) -> CommandLifecycleState:
        if current is not None:
            if current.status is CommandExecutionStatus.SUCCEEDED:
                return CommandLifecycleState.SUCCEEDED
            if attempts:
                return CommandLifecycleState.RETRY_REJECTED
            return CommandLifecycleState.REJECTED
        if recoveries:
            return CommandLifecycleState.READY_FOR_RETRY
        if archived:
            return CommandLifecycleState.REJECTED
        return CommandLifecycleState.NOT_FOUND
