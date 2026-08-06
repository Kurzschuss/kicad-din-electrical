"""Administrative Diagnose und Wiederaufnahme abgelehnter ProjectOS-Commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .identifiers import BusinessId
from .project_command_history import (
    CommandExecutionRecord,
    CommandExecutionStatus,
    SQLiteCommandExecutionRepository,
)


@dataclass(frozen=True, slots=True)
class CommandExecutionDiagnostic:
    total: int
    succeeded: int
    rejected: int


@dataclass(frozen=True, slots=True)
class CommandRecoveryRecord:
    recovery_id: BusinessId
    command_id: BusinessId
    actor_id: BusinessId
    reason: str
    recovered_at: datetime

    def __post_init__(self) -> None:
        reason = self.reason.strip()
        if not reason:
            raise ValueError("Eine Command-Wiederaufnahme benötigt eine Begründung.")
        if self.recovered_at.tzinfo is None:
            raise ValueError("recovered_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "recovered_at", self.recovered_at.astimezone(timezone.utc))


class CommandAdministrationService:
    """Liefert Diagnosewerte und gibt abgelehnte Commands kontrolliert erneut frei."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        history: SQLiteCommandExecutionRepository,
    ) -> None:
        self._connection = connection
        self._history = history
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_command_recoveries (
                recovery_id TEXT PRIMARY KEY,
                command_id TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                recovered_at TEXT NOT NULL
            )
            """
        )

    def diagnostic(self) -> CommandExecutionDiagnostic:
        records = self._history.all()
        return CommandExecutionDiagnostic(
            total=len(records),
            succeeded=sum(record.status is CommandExecutionStatus.SUCCEEDED for record in records),
            rejected=sum(record.status is CommandExecutionStatus.REJECTED for record in records),
        )

    def get(self, command_id: BusinessId) -> CommandExecutionRecord | None:
        """Lädt den aktuellen persistenten Status eines Commands."""
        return self._history.get(command_id)

    def list_by_status(
        self, status: CommandExecutionStatus
    ) -> tuple[CommandExecutionRecord, ...]:
        return tuple(record for record in self._history.all() if record.status is status)

    def recover_rejected(
        self,
        command_id: BusinessId,
        *,
        recovery_id: BusinessId,
        actor_id: BusinessId,
        reason: str,
        recovered_at: datetime,
    ) -> CommandRecoveryRecord:
        record = self._history.get(command_id)
        if record is None:
            raise LookupError("ERR-PRJ-CMD-0006: Command wurde nicht gefunden.")
        if record.status is not CommandExecutionStatus.REJECTED:
            raise ValueError("ERR-PRJ-CMD-0007: Nur abgelehnte Commands können wiederaufgenommen werden.")
        recovery = CommandRecoveryRecord(
            recovery_id=recovery_id,
            command_id=command_id,
            actor_id=actor_id,
            reason=reason,
            recovered_at=recovered_at,
        )
        try:
            self._connection.execute(
                """
                INSERT INTO projectos_command_recoveries(
                    recovery_id, command_id, actor_id, reason, recovered_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(recovery.recovery_id), str(recovery.command_id),
                    str(recovery.actor_id), recovery.reason, recovery.recovered_at.isoformat(),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-PRJ-CMD-0008: Wiederaufnahme-ID wurde bereits verwendet.") from exc
        self._connection.execute(
            "DELETE FROM projectos_command_executions WHERE command_id = ? AND status = ?",
            (str(command_id), CommandExecutionStatus.REJECTED.value),
        )
        return recovery

    def recoveries(self) -> tuple[CommandRecoveryRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_command_recoveries ORDER BY recovered_at, recovery_id"
        ).fetchall()
        return tuple(
            CommandRecoveryRecord(
                recovery_id=BusinessId.parse(row["recovery_id"]),
                command_id=BusinessId.parse(row["command_id"]),
                actor_id=BusinessId.parse(row["actor_id"]),
                reason=row["reason"],
                recovered_at=datetime.fromisoformat(row["recovered_at"]),
            )
            for row in rows
        )
