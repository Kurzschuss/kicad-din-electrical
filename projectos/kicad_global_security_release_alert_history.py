"""Persistente Alarme für abgelehnte globale Besetzungsfreigabeversuche."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json, sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_attempt_alert import GlobalSecurityStaffingReleaseAttemptAlertResult, GlobalSecurityStaffingReleaseAlertLevel

class GlobalSecurityStaffingReleaseAlertStatus(StrEnum):
    OPEN="OPEN"; ACKNOWLEDGED="ACKNOWLEDGED"; RESOLVED="RESOLVED"

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertRecord:
    alert_id: BusinessId; level: GlobalSecurityStaffingReleaseAlertLevel; status: GlobalSecurityStaffingReleaseAlertStatus
    created_at: datetime; window_start: datetime; total_attempts: int; attempts_without_actor: int
    finding_codes: tuple[str,...]; correlation_id: CorrelationId
    acknowledged_at: datetime|None=None; acknowledged_by: BusinessId|None=None; acknowledgement_reason: str|None=None
    resolved_at: datetime|None=None; resolved_by: BusinessId|None=None; resolution_reason: str|None=None

class SQLiteGlobalSecurityStaffingReleaseAlertRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection=connection
        connection.execute("""CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_alerts (
        alert_id TEXT PRIMARY KEY, level TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
        window_start TEXT NOT NULL, total_attempts INTEGER NOT NULL, attempts_without_actor INTEGER NOT NULL,
        finding_codes_json TEXT NOT NULL, correlation_id TEXT NOT NULL, acknowledged_at TEXT, acknowledged_by TEXT,
        acknowledgement_reason TEXT, resolved_at TEXT, resolved_by TEXT, resolution_reason TEXT)""")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_global_staffing_release_alert_status ON projectos_global_security_staffing_release_alerts(status,created_at DESC,alert_id DESC)")
        connection.commit()
    def create(self, *, alert_id: BusinessId, result: GlobalSecurityStaffingReleaseAttemptAlertResult, correlation_id: CorrelationId):
        if not result.alert: raise ValueError("ERR-KICAD-0168: Ein CLEAR-Ergebnis darf nicht als Alarm gespeichert werden.")
        for value in (result.evaluated_at,result.window_start):
            if value.tzinfo is None or value.utcoffset() is None: raise ValueError("ERR-KICAD-0169: Alarmzeitpunkte benötigen eine Zeitzone.")
        try:
            self._connection.execute("INSERT INTO projectos_global_security_staffing_release_alerts (alert_id,level,status,created_at,window_start,total_attempts,attempts_without_actor,finding_codes_json,correlation_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (str(alert_id),result.level.value,GlobalSecurityStaffingReleaseAlertStatus.OPEN.value,result.evaluated_at.isoformat(),result.window_start.isoformat(),result.total_attempts,result.attempts_without_actor,json.dumps(tuple(x.code for x in result.findings),separators=(",",":")),str(correlation_id)))
            self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0170: Die Alarmkennung ist bereits vorhanden.") from exc
        return self.get(alert_id)
    def acknowledge(self, alert_id: BusinessId, *, acknowledged_at: datetime, acknowledged_by: BusinessId, reason: str):
        record=self.get(alert_id)
        if record.status is not GlobalSecurityStaffingReleaseAlertStatus.OPEN: raise ValueError("ERR-KICAD-0171: Nur ein offener Alarm kann bestätigt werden.")
        instant,normalized=_validate_action(acknowledged_at,reason)
        if instant<record.created_at: raise ValueError("ERR-KICAD-0172: Die Bestätigung darf nicht vor der Alarmerzeugung liegen.")
        self._connection.execute("UPDATE projectos_global_security_staffing_release_alerts SET status=?,acknowledged_at=?,acknowledged_by=?,acknowledgement_reason=? WHERE alert_id=?",(GlobalSecurityStaffingReleaseAlertStatus.ACKNOWLEDGED.value,instant.isoformat(),str(acknowledged_by),normalized,str(alert_id))); self._connection.commit(); return self.get(alert_id)
    def resolve(self, alert_id: BusinessId, *, resolved_at: datetime, resolved_by: BusinessId, reason: str):
        record=self.get(alert_id)
        if record.status is not GlobalSecurityStaffingReleaseAlertStatus.ACKNOWLEDGED: raise ValueError("ERR-KICAD-0173: Nur ein bestätigter Alarm kann abgeschlossen werden.")
        instant,normalized=_validate_action(resolved_at,reason)
        if record.acknowledged_at is None or instant<record.acknowledged_at: raise ValueError("ERR-KICAD-0174: Der Abschluss darf nicht vor der Bestätigung liegen.")
        self._connection.execute("UPDATE projectos_global_security_staffing_release_alerts SET status=?,resolved_at=?,resolved_by=?,resolution_reason=? WHERE alert_id=?",(GlobalSecurityStaffingReleaseAlertStatus.RESOLVED.value,instant.isoformat(),str(resolved_by),normalized,str(alert_id))); self._connection.commit(); return self.get(alert_id)
    def get(self, alert_id: BusinessId):
        row=self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alerts WHERE alert_id=?",(str(alert_id),)).fetchone()
        if row is None: raise ValueError("ERR-KICAD-0175: Sicherheitsalarm wurde nicht gefunden.")
        return _decode(row)
    def list_for_status(self,status: GlobalSecurityStaffingReleaseAlertStatus):
        return tuple(_decode(r) for r in self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alerts WHERE status=? ORDER BY created_at DESC,alert_id DESC",(status.value,)).fetchall())

def _validate_action(at: datetime, reason: str):
    if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0176: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
    normalized=reason.strip()
    if not normalized: raise ValueError("ERR-KICAD-0177: Die Alarmbearbeitung benötigt eine Begründung.")
    return at,normalized

def _decode(row):
    return GlobalSecurityStaffingReleaseAlertRecord(BusinessId(str(row[0])),GlobalSecurityStaffingReleaseAlertLevel(str(row[1])),GlobalSecurityStaffingReleaseAlertStatus(str(row[2])),datetime.fromisoformat(str(row[3])),datetime.fromisoformat(str(row[4])),int(row[5]),int(row[6]),tuple(json.loads(str(row[7]))),CorrelationId(str(row[8])),datetime.fromisoformat(str(row[9])) if row[9] else None,BusinessId(str(row[10])) if row[10] else None,str(row[11]) if row[11] else None,datetime.fromisoformat(str(row[12])) if row[12] else None,BusinessId(str(row[13])) if row[13] else None,str(row[14]) if row[14] else None)
