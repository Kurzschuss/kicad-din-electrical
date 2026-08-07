"""Unveränderliches Audit abgelehnter globaler Besetzungsfreigabeversuche."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .identifiers import BusinessId, CorrelationId


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAttemptRecord:
    attempt_id: BusinessId
    attempted_at: datetime
    actor_id: BusinessId | None
    acting_role: BusinessId
    permission_id: BusinessId
    denial_code: str
    denial_reason: str
    correlation_id: CorrelationId


class SQLiteGlobalSecurityStaffingReleaseAttemptRepository:
    """Nur anhängbare Historie abgelehnter Besetzungsfreigabeversuche."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_attempt_audit (
                attempt_id TEXT PRIMARY KEY,
                attempted_at TEXT NOT NULL,
                actor_id TEXT,
                acting_role TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                denial_code TEXT NOT NULL,
                denial_reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_global_staffing_release_attempt_time "
            "ON projectos_global_security_staffing_release_attempt_audit(attempted_at DESC, attempt_id DESC)"
        )
        self._connection.commit()

    def append(self, record: GlobalSecurityStaffingReleaseAttemptRecord) -> GlobalSecurityStaffingReleaseAttemptRecord:
        if record.attempted_at.tzinfo is None or record.attempted_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0148: Der Versuchszeitpunkt benötigt eine Zeitzone.")
        code = record.denial_code.strip().upper()
        reason = record.denial_reason.strip()
        if not code:
            raise ValueError("ERR-KICAD-0149: Der Ablehnungscode fehlt.")
        if not reason:
            raise ValueError("ERR-KICAD-0150: Die Ablehnungsbegründung fehlt.")
        try:
            self._connection.execute(
                "INSERT INTO projectos_global_security_staffing_release_attempt_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (str(record.attempt_id), record.attempted_at.astimezone(timezone.utc).isoformat(),
                 str(record.actor_id) if record.actor_id else None, str(record.acting_role),
                 str(record.permission_id), code, reason, str(record.correlation_id)),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0151: Die Versuchskennung ist bereits vorhanden.") from exc
        return self.get(record.attempt_id)

    def get(self, attempt_id: BusinessId) -> GlobalSecurityStaffingReleaseAttemptRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_global_security_staffing_release_attempt_audit WHERE attempt_id = ?",
            (str(attempt_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0152: Der Freigabeversuch wurde nicht gefunden.")
        return GlobalSecurityStaffingReleaseAttemptRecord(
            BusinessId(str(row[0])), datetime.fromisoformat(str(row[1])),
            BusinessId(str(row[2])) if row[2] else None, BusinessId(str(row[3])),
            BusinessId(str(row[4])), str(row[5]), str(row[6]), CorrelationId(str(row[7])),
        )

    def list_all(self) -> tuple[GlobalSecurityStaffingReleaseAttemptRecord, ...]:
        rows = self._connection.execute(
            "SELECT attempt_id FROM projectos_global_security_staffing_release_attempt_audit "
            "ORDER BY attempted_at DESC, attempt_id DESC"
        ).fetchall()
        return tuple(self.get(BusinessId(str(row[0]))) for row in rows)
