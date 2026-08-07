"""Verknüpfte Wiederholungsverarbeitung administrativ freigegebener Commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .application import Command
from .identifiers import BusinessId, ObjectId
from .project_command_admin import CommandAdministrationService, CommandRecoveryRecord
from .project_command_history import (
    CommandExecutionStatus,
    IdempotentProjectCommandPipeline,
    IdempotentProjectCommandResult,
)
from .results import MessageSeverity, Result, ResultMessage


@dataclass(frozen=True, slots=True)
class CommandRetryRecord:
    attempt_id: BusinessId
    command_id: BusinessId
    recovery_id: BusinessId
    status: CommandExecutionStatus
    processed_at: datetime
    correlation_id: str

    def __post_init__(self) -> None:
        if self.processed_at.tzinfo is None:
            raise ValueError("processed_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "processed_at", self.processed_at.astimezone(timezone.utc))


@dataclass(frozen=True, slots=True)
class RecoveredCommandExecutionResult:
    recovery: CommandRecoveryRecord
    retry: CommandRetryRecord
    execution: IdempotentProjectCommandResult | None


class RecoveredCommandExecutionService:
    """Verarbeitet einen freigegebenen Command erneut und dokumentiert die Kette."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        administration: CommandAdministrationService,
        pipeline: IdempotentProjectCommandPipeline,
    ) -> None:
        self._connection = connection
        self._administration = administration
        self._pipeline = pipeline
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_command_retry_attempts (
                attempt_id TEXT PRIMARY KEY,
                command_id TEXT NOT NULL,
                recovery_id TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL
            )
            """
        )

    def execute(
        self,
        command: Command,
        *,
        recovery_id: BusinessId,
        attempt_id: BusinessId,
        project_id: BusinessId,
        project_object_id: ObjectId,
        audit_id: BusinessId,
        reason: str,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> Result[RecoveredCommandExecutionResult]:
        recovery = self._administration.get_recovery(recovery_id)
        if recovery is None:
            return self._failure("ERR-PRJ-CMD-0009", "Wiederaufnahme wurde nicht gefunden.", command)
        if recovery.command_id != command.command_id:
            return self._failure(
                "ERR-PRJ-CMD-0010",
                "Die Wiederaufnahme gehört nicht zu diesem Command.",
                command,
            )
        existing = self._connection.execute(
            "SELECT 1 FROM projectos_command_retry_attempts WHERE recovery_id = ?",
            (str(recovery_id),),
        ).fetchone()
        if existing is not None:
            return self._failure(
                "ERR-PRJ-CMD-0011",
                "Für diese Wiederaufnahme wurde bereits ein Folgeversuch dokumentiert.",
                command,
            )

        result = self._pipeline.dispatch(
            command,
            project_id=project_id,
            project_object_id=project_object_id,
            audit_id=audit_id,
            reason=reason,
            unavailable_user_ids=unavailable_user_ids,
        )
        status = CommandExecutionStatus.SUCCEEDED if result.is_success else CommandExecutionStatus.REJECTED
        retry = CommandRetryRecord(
            attempt_id=attempt_id,
            command_id=command.command_id,
            recovery_id=recovery_id,
            status=status,
            processed_at=datetime.now(timezone.utc),
            correlation_id=str(command.correlation_id),
        )
        try:
            self._connection.execute(
                """
                INSERT INTO projectos_command_retry_attempts(
                    attempt_id, command_id, recovery_id, status, processed_at, correlation_id
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(retry.attempt_id), str(retry.command_id), str(retry.recovery_id),
                 retry.status.value, retry.processed_at.isoformat(), retry.correlation_id),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-PRJ-CMD-0012: Folgeversuchs-ID wurde bereits verwendet.") from exc

        if not result.is_success:
            return Result.failure(*result.messages, correlation_id=command.correlation_id)
        return Result.success(
            RecoveredCommandExecutionResult(recovery, retry, result.value),
            correlation_id=command.correlation_id,
        )

    def attempts(self, command_id: BusinessId | None = None) -> tuple[CommandRetryRecord, ...]:
        if command_id is None:
            rows = self._connection.execute(
                "SELECT * FROM projectos_command_retry_attempts ORDER BY processed_at, attempt_id"
            ).fetchall()
        else:
            rows = self._connection.execute(
                """SELECT * FROM projectos_command_retry_attempts
                   WHERE command_id = ? ORDER BY processed_at, attempt_id""",
                (str(command_id),),
            ).fetchall()
        return tuple(
            CommandRetryRecord(
                attempt_id=BusinessId.parse(row["attempt_id"]),
                command_id=BusinessId.parse(row["command_id"]),
                recovery_id=BusinessId.parse(row["recovery_id"]),
                status=CommandExecutionStatus(row["status"]),
                processed_at=datetime.fromisoformat(row["processed_at"]),
                correlation_id=row["correlation_id"],
            )
            for row in rows
        )

    @staticmethod
    def _failure(code: str, text: str, command: Command) -> Result[RecoveredCommandExecutionResult]:
        return Result.failure(
            ResultMessage(BusinessId(code), MessageSeverity.ERROR, text),
            correlation_id=command.correlation_id,
        )
