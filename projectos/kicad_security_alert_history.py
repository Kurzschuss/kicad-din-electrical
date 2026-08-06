"""Persistente KiCad-Sicherheitsalarme mit Bestätigung und Abschluss."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_release_attempt_alert import (
    KiCadReleaseAttemptAlertResult,
    KiCadSecurityAlertLevel,
)


class KiCadSecurityAlertStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True, slots=True)
class KiCadSecurityAlertRecord:
    alert_id: BusinessId
    project_id: BusinessId | None
    level: KiCadSecurityAlertLevel
    status: KiCadSecurityAlertStatus
    created_at: datetime
    window_start: datetime
    total_attempts: int
    finding_codes: tuple[str, ...]
    correlation_id: CorrelationId
    acknowledged_at: datetime | None = None
    acknowledged_by: BusinessId | None = None
    acknowledgement_reason: str | None = None
    resolved_at: datetime | None = None
    resolved_by: BusinessId | None = None
    resolution_reason: str | None = None


class SQLiteKiCadSecurityAlertRepository:
    """Speichert Sicherheitsalarme und deren dokumentierten Lebenszyklus."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_kicad_security_alerts (
                alert_id TEXT PRIMARY KEY,
                project_id TEXT,
                level TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                window_start TEXT NOT NULL,
                total_attempts INTEGER NOT NULL,
                finding_codes_json TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                acknowledged_at TEXT,
                acknowledged_by TEXT,
                acknowledgement_reason TEXT,
                resolved_at TEXT,
                resolved_by TEXT,
                resolution_reason TEXT
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_kicad_security_alert_status_time "
            "ON projectos_kicad_security_alerts(status, created_at DESC, alert_id DESC)"
        )
        self._connection.commit()

    def create(
        self,
        *,
        alert_id: BusinessId,
        result: KiCadReleaseAttemptAlertResult,
        correlation_id: CorrelationId,
    ) -> KiCadSecurityAlertRecord:
        if not result.alert:
            raise ValueError("ERR-KICAD-0100: Ein CLEAR-Ergebnis darf nicht als Alarm gespeichert werden.")
        for value in (result.evaluated_at, result.window_start):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("ERR-KICAD-0101: Alarmzeitpunkte benötigen eine Zeitzone.")
        codes = tuple(item.code for item in result.findings)
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_security_alerts "
                "(alert_id, project_id, level, status, created_at, window_start, total_attempts, finding_codes_json, correlation_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(alert_id), str(result.project_id) if result.project_id else None,
                    result.level.value, KiCadSecurityAlertStatus.OPEN.value,
                    result.evaluated_at.isoformat(), result.window_start.isoformat(), result.total_attempts,
                    json.dumps(codes, ensure_ascii=False, separators=(",", ":")), str(correlation_id),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0102: Die Alarmkennung ist bereits vorhanden.") from exc
        return self.get(alert_id)

    def acknowledge(
        self,
        alert_id: BusinessId,
        *,
        acknowledged_at: datetime,
        acknowledged_by: BusinessId,
        reason: str,
    ) -> KiCadSecurityAlertRecord:
        record = self.get(alert_id)
        if record.status is not KiCadSecurityAlertStatus.OPEN:
            raise ValueError("ERR-KICAD-0103: Nur ein offener Alarm kann bestätigt werden.")
        instant, normalized = _validate_action(acknowledged_at, reason)
        if instant < record.created_at:
            raise ValueError("ERR-KICAD-0104: Die Bestätigung darf nicht vor der Alarmerzeugung liegen.")
        self._connection.execute(
            "UPDATE projectos_kicad_security_alerts SET status = ?, acknowledged_at = ?, acknowledged_by = ?, acknowledgement_reason = ? WHERE alert_id = ?",
            (KiCadSecurityAlertStatus.ACKNOWLEDGED.value, instant.isoformat(), str(acknowledged_by), normalized, str(alert_id)),
        )
        self._connection.commit()
        return self.get(alert_id)

    def resolve(
        self,
        alert_id: BusinessId,
        *,
        resolved_at: datetime,
        resolved_by: BusinessId,
        reason: str,
    ) -> KiCadSecurityAlertRecord:
        record = self.get(alert_id)
        if record.status is not KiCadSecurityAlertStatus.ACKNOWLEDGED:
            raise ValueError("ERR-KICAD-0105: Nur ein bestätigter Alarm kann abgeschlossen werden.")
        instant, normalized = _validate_action(resolved_at, reason)
        assert record.acknowledged_at is not None
        if instant < record.acknowledged_at:
            raise ValueError("ERR-KICAD-0106: Der Abschluss darf nicht vor der Bestätigung liegen.")
        self._connection.execute(
            "UPDATE projectos_kicad_security_alerts SET status = ?, resolved_at = ?, resolved_by = ?, resolution_reason = ? WHERE alert_id = ?",
            (KiCadSecurityAlertStatus.RESOLVED.value, instant.isoformat(), str(resolved_by), normalized, str(alert_id)),
        )
        self._connection.commit()
        return self.get(alert_id)

    def get(self, alert_id: BusinessId) -> KiCadSecurityAlertRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_kicad_security_alerts WHERE alert_id = ?", (str(alert_id),)
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0107: Sicherheitsalarm wurde nicht gefunden.")
        return _decode_record(row)

    def list_for_status(self, status: KiCadSecurityAlertStatus) -> tuple[KiCadSecurityAlertRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_security_alerts WHERE status = ? ORDER BY created_at DESC, alert_id DESC",
            (status.value,),
        ).fetchall()
        return tuple(_decode_record(row) for row in rows)


def _validate_action(at: datetime, reason: str) -> tuple[datetime, str]:
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("ERR-KICAD-0108: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
    normalized = reason.strip()
    if not normalized:
        raise ValueError("ERR-KICAD-0109: Die Alarmbearbeitung benötigt eine Begründung.")
    return at, normalized


def _decode_record(row: tuple[object, ...]) -> KiCadSecurityAlertRecord:
    return KiCadSecurityAlertRecord(
        alert_id=BusinessId(str(row[0])),
        project_id=BusinessId(str(row[1])) if row[1] else None,
        level=KiCadSecurityAlertLevel(str(row[2])),
        status=KiCadSecurityAlertStatus(str(row[3])),
        created_at=datetime.fromisoformat(str(row[4])),
        window_start=datetime.fromisoformat(str(row[5])),
        total_attempts=int(row[6]),
        finding_codes=tuple(json.loads(str(row[7]))),
        correlation_id=CorrelationId(str(row[8])),
        acknowledged_at=datetime.fromisoformat(str(row[9])) if row[9] else None,
        acknowledged_by=BusinessId(str(row[10])) if row[10] else None,
        acknowledgement_reason=str(row[11]) if row[11] else None,
        resolved_at=datetime.fromisoformat(str(row[12])) if row[12] else None,
        resolved_by=BusinessId(str(row[13])) if row[13] else None,
        resolution_reason=str(row[14]) if row[14] else None,
    )
