"""Unveränderliches Audit abgelehnter Bearbeitungsversuche globaler Besetzungsfreigabealarme."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_alert_authorization import GlobalSecurityStaffingReleaseAlertAction

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertActionAttemptRecord:
    attempt_id: BusinessId
    alert_id: BusinessId
    action: GlobalSecurityStaffingReleaseAlertAction
    attempted_at: datetime
    actor_id: BusinessId | None
    acting_role: BusinessId
    permission_id: BusinessId
    denial_code: str
    denial_reason: str
    correlation_id: CorrelationId

class SQLiteGlobalSecurityStaffingReleaseAlertActionAttemptRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection=connection
        connection.execute("""CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_alert_action_attempt_audit (
        attempt_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL, attempted_at TEXT NOT NULL,
        actor_id TEXT, acting_role TEXT NOT NULL, permission_id TEXT NOT NULL, denial_code TEXT NOT NULL,
        denial_reason TEXT NOT NULL, correlation_id TEXT NOT NULL)""")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_global_staffing_alert_attempt ON projectos_global_security_staffing_release_alert_action_attempt_audit(alert_id,attempted_at DESC,attempt_id DESC)")
        connection.commit()
    def append(self, record: GlobalSecurityStaffingReleaseAlertActionAttemptRecord):
        if record.attempted_at.tzinfo is None or record.attempted_at.utcoffset() is None: raise ValueError("ERR-KICAD-0183: Der Versuchszeitpunkt benötigt eine Zeitzone.")
        code=record.denial_code.strip().upper(); reason=record.denial_reason.strip()
        if not code: raise ValueError("ERR-KICAD-0184: Der Ablehnungscode fehlt.")
        if not reason: raise ValueError("ERR-KICAD-0185: Die Ablehnungsbegründung fehlt.")
        try:
            self._connection.execute("INSERT INTO projectos_global_security_staffing_release_alert_action_attempt_audit VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.attempt_id),str(record.alert_id),record.action.value,record.attempted_at.astimezone(timezone.utc).isoformat(),str(record.actor_id) if record.actor_id else None,str(record.acting_role),str(record.permission_id),code,reason,str(record.correlation_id)))
            self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0186: Die Versuchskennung ist bereits vorhanden.") from exc
        return self.get(record.attempt_id)
    def get(self, attempt_id: BusinessId):
        row=self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alert_action_attempt_audit WHERE attempt_id=?",(str(attempt_id),)).fetchone()
        if row is None: raise ValueError("ERR-KICAD-0187: Der Bearbeitungsversuch wurde nicht gefunden.")
        return _decode(row)
    def list_for_alert(self, alert_id: BusinessId):
        return tuple(_decode(r) for r in self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alert_action_attempt_audit WHERE alert_id=? ORDER BY attempted_at DESC,attempt_id DESC",(str(alert_id),)).fetchall())

def _decode(row):
    return GlobalSecurityStaffingReleaseAlertActionAttemptRecord(BusinessId(str(row[0])),BusinessId(str(row[1])),GlobalSecurityStaffingReleaseAlertAction(str(row[2])),datetime.fromisoformat(str(row[3])),BusinessId(str(row[4])) if row[4] else None,BusinessId(str(row[5])),BusinessId(str(row[6])),str(row[7]),str(row[8]),CorrelationId(str(row[9])))
