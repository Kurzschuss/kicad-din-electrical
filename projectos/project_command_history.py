"""Persistente Command-Ausführungshistorie und Idempotenzschutz."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import sqlite3

from .application import Command
from .identifiers import BusinessId, ObjectId
from .project_commands import ProjectCommandExecutionResult, ProjectCommandPipeline
from .results import MessageSeverity, Result, ResultMessage


class CommandExecutionStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class CommandExecutionRecord:
    command_id: BusinessId
    command_type: str
    project_id: BusinessId
    project_object_id: ObjectId
    payload_hash: str
    status: CommandExecutionStatus
    processed_at: datetime
    correlation_id: str
    message_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.processed_at.tzinfo is None:
            raise ValueError("processed_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "processed_at", self.processed_at.astimezone(timezone.utc))
        object.__setattr__(self, "message_codes", tuple(self.message_codes))


@dataclass(frozen=True, slots=True)
class IdempotentProjectCommandResult:
    record: CommandExecutionRecord
    replayed: bool
    execution: ProjectCommandExecutionResult[object] | None = None


class SQLiteCommandExecutionRepository:
    """Append-only-Historie mit eindeutiger Command-ID."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_command_executions (
                command_id TEXT PRIMARY KEY,
                command_type TEXT NOT NULL,
                project_id TEXT NOT NULL,
                project_object_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                message_codes TEXT NOT NULL
            )
            """
        )

    def get(self, command_id: BusinessId) -> CommandExecutionRecord | None:
        row = self._connection.execute(
            "SELECT * FROM projectos_command_executions WHERE command_id = ?",
            (str(command_id),),
        ).fetchone()
        return None if row is None else self._decode(row)

    def append(self, record: CommandExecutionRecord) -> CommandExecutionRecord:
        try:
            self._connection.execute(
                """
                INSERT INTO projectos_command_executions(
                    command_id, command_type, project_id, project_object_id, payload_hash,
                    status, processed_at, correlation_id, message_codes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.command_id), record.command_type, str(record.project_id),
                    str(record.project_object_id), record.payload_hash, record.status.value,
                    record.processed_at.isoformat(), record.correlation_id,
                    json.dumps(record.message_codes, ensure_ascii=False),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-PRJ-CMD-0005: Command-ID wurde bereits verarbeitet.") from exc
        return record

    def all(self) -> tuple[CommandExecutionRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_command_executions ORDER BY processed_at, command_id"
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    @staticmethod
    def _decode(row: sqlite3.Row) -> CommandExecutionRecord:
        return CommandExecutionRecord(
            command_id=BusinessId.parse(row["command_id"]),
            command_type=row["command_type"],
            project_id=BusinessId.parse(row["project_id"]),
            project_object_id=ObjectId.parse(row["project_object_id"]),
            payload_hash=row["payload_hash"],
            status=CommandExecutionStatus(row["status"]),
            processed_at=datetime.fromisoformat(row["processed_at"]),
            correlation_id=row["correlation_id"],
            message_codes=tuple(json.loads(row["message_codes"])),
        )


def command_fingerprint(command: Command, project_id: BusinessId, project_object_id: ObjectId) -> str:
    data = {
        "command_type": command.command_type,
        "project_id": str(project_id),
        "project_object_id": str(project_object_id),
        "payload": dict(command.payload),
        "expected_revision": command.expected_revision,
    }
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class IdempotentProjectCommandPipeline:
    """Verhindert doppelte oder widersprüchliche Verarbeitung derselben Command-ID."""

    def __init__(
        self,
        pipeline: ProjectCommandPipeline,
        history: SQLiteCommandExecutionRepository,
    ) -> None:
        self._pipeline = pipeline
        self._history = history

    def dispatch(
        self,
        command: Command,
        *,
        project_id: BusinessId,
        project_object_id: ObjectId,
        audit_id: BusinessId,
        reason: str,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> Result[IdempotentProjectCommandResult]:
        fingerprint = command_fingerprint(command, project_id, project_object_id)
        existing = self._history.get(command.command_id)
        if existing is not None:
            if existing.payload_hash != fingerprint:
                return Result.failure(
                    ResultMessage(
                        BusinessId("ERR-PRJ-CMD-0004"),
                        MessageSeverity.ERROR,
                        "Die Command-ID wurde bereits mit abweichendem Inhalt verarbeitet.",
                    ),
                    correlation_id=command.correlation_id,
                )
            return Result.success(
                IdempotentProjectCommandResult(existing, replayed=True),
                correlation_id=command.correlation_id,
            )

        result = self._pipeline.dispatch(
            command,
            project_id=project_id,
            project_object_id=project_object_id,
            audit_id=audit_id,
            reason=reason,
            unavailable_user_ids=unavailable_user_ids,
        )
        record = CommandExecutionRecord(
            command_id=command.command_id,
            command_type=command.command_type,
            project_id=project_id,
            project_object_id=project_object_id,
            payload_hash=fingerprint,
            status=(CommandExecutionStatus.SUCCEEDED if result.is_success else CommandExecutionStatus.REJECTED),
            processed_at=datetime.now(timezone.utc),
            correlation_id=str(command.correlation_id),
            message_codes=tuple(str(message.code) for message in result.messages),
        )
        self._history.append(record)
        if not result.is_success:
            return Result.failure(*result.messages, correlation_id=command.correlation_id)
        assert result.value is not None
        return Result.success(
            IdempotentProjectCommandResult(record, replayed=False, execution=result.value),
            correlation_id=command.correlation_id,
        )
