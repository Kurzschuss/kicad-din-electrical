"""Unveränderliches Sicherheitsaudit abgelehnter KiCad-Freigabeversuche."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import sqlite3

from .identifiers import BusinessId, CorrelationId


@dataclass(frozen=True, slots=True)
class KiCadReleaseAttemptAuditRecord:
    attempt_id: BusinessId
    project_id: BusinessId
    attempted_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    denial_code: str
    denial_reason: str
    correlation_id: CorrelationId


class SQLiteKiCadReleaseAttemptAuditRepository:
    """Nur anhängbare Historie abgelehnter Freigabeversuche."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_kicad_release_attempt_audit (
                attempt_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                acting_role TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                denial_code TEXT NOT NULL,
                denial_reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_kicad_release_attempt_project_time "
            "ON projectos_kicad_release_attempt_audit(project_id, attempted_at DESC, attempt_id DESC)"
        )
        self._connection.commit()

    def append(
        self,
        *,
        attempt_id: BusinessId,
        project_id: BusinessId,
        attempted_at: datetime,
        actor_id: BusinessId,
        acting_role: BusinessId,
        permission_id: BusinessId,
        denial_code: str,
        denial_reason: str,
        correlation_id: CorrelationId,
    ) -> KiCadReleaseAttemptAuditRecord:
        if attempted_at.tzinfo is None or attempted_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0080: Der Versuchszeitpunkt benötigt eine Zeitzone.")
        code = denial_code.strip().upper()
        reason = denial_reason.strip()
        if not code:
            raise ValueError("ERR-KICAD-0081: Ein abgelehnter Freigabeversuch benötigt einen Ablehnungscode.")
        if not reason:
            raise ValueError("ERR-KICAD-0082: Ein abgelehnter Freigabeversuch benötigt eine Begründung.")
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_release_attempt_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(attempt_id), str(project_id), attempted_at.isoformat(), str(actor_id),
                    str(acting_role), str(permission_id), code, reason, str(correlation_id),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0083: Die Freigabeversuchskennung ist bereits vorhanden.") from exc
        return self.get(attempt_id)

    def get(self, attempt_id: BusinessId) -> KiCadReleaseAttemptAuditRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_kicad_release_attempt_audit WHERE attempt_id = ?",
            (str(attempt_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0084: Freigabeversuch wurde nicht gefunden.")
        return _decode_record(row)

    def list_for_project(self, project_id: BusinessId) -> tuple[KiCadReleaseAttemptAuditRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_release_attempt_audit WHERE project_id = ? "
            "ORDER BY attempted_at DESC, attempt_id DESC",
            (str(project_id),),
        ).fetchall()
        return tuple(_decode_record(row) for row in rows)


def _decode_record(row: tuple[object, ...]) -> KiCadReleaseAttemptAuditRecord:
    return KiCadReleaseAttemptAuditRecord(
        attempt_id=BusinessId(str(row[0])),
        project_id=BusinessId(str(row[1])),
        attempted_at=datetime.fromisoformat(str(row[2])),
        actor_id=BusinessId(str(row[3])),
        acting_role=BusinessId(str(row[4])),
        permission_id=BusinessId(str(row[5])),
        denial_code=str(row[6]),
        denial_reason=str(row[7]),
        correlation_id=CorrelationId(str(row[8])),
    )
