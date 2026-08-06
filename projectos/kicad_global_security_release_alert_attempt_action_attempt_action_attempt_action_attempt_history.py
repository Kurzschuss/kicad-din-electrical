"""Persistente Alarmereignisse fuer die Alarmbewertung aus AP-0109."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json, sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_alert import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel as Level,
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptAlertResult as Result,
)

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus(StrEnum):
    OPEN="OPEN"; ACKNOWLEDGED="ACKNOWLEDGED"; RESOLVED="RESOLVED"

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord:
    alert_id:BusinessId; level:Level; status:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus
    created_at:datetime; window_start:datetime; total_attempts:int; acknowledge_attempts:int; resolve_attempts:int; attempts_without_actor:int
    finding_codes:tuple[str,...]; correlation_id:CorrelationId
    acknowledged_at:datetime|None=None; acknowledged_by:BusinessId|None=None; acknowledgement_reason:str|None=None
    resolved_at:datetime|None=None; resolved_by:BusinessId|None=None; resolution_reason:str|None=None

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_alerts"
    def __init__(self,connection:sqlite3.Connection):
        self._connection=connection
        connection.execute(f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (alert_id TEXT PRIMARY KEY,level TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,window_start TEXT NOT NULL,total_attempts INTEGER NOT NULL,acknowledge_attempts INTEGER NOT NULL,resolve_attempts INTEGER NOT NULL,attempts_without_actor INTEGER NOT NULL,finding_codes_json TEXT NOT NULL,correlation_id TEXT NOT NULL,acknowledged_at TEXT,acknowledged_by TEXT,acknowledgement_reason TEXT,resolved_at TEXT,resolved_by TEXT,resolution_reason TEXT)""")
        connection.execute(f"CREATE INDEX IF NOT EXISTS idx_ap0110_status ON {self.TABLE}(status,created_at DESC,alert_id DESC)"); connection.commit()
    def create(self,*,alert_id:BusinessId,result:Result,correlation_id:CorrelationId):
        if not result.alert: raise ValueError("ERR-KICAD-0316: Ein CLEAR-Ergebnis darf nicht gespeichert werden.")
        for value in (result.evaluated_at,result.window_start):
            if value.tzinfo is None or value.utcoffset() is None: raise ValueError("ERR-KICAD-0317: Alarmzeitpunkte benoetigen eine Zeitzone.")
        try:
            self._connection.execute(f"INSERT INTO {self.TABLE} (alert_id,level,status,created_at,window_start,total_attempts,acknowledge_attempts,resolve_attempts,attempts_without_actor,finding_codes_json,correlation_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(str(alert_id),result.level.value,"OPEN",result.evaluated_at.isoformat(),result.window_start.isoformat(),result.total_attempts,result.acknowledge_attempts,result.resolve_attempts,result.attempts_without_actor,json.dumps(tuple(x.code for x in result.findings),separators=(",",":")),str(correlation_id))); self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0318: Die Alarmkennung ist bereits vorhanden.") from exc
        return self.get(alert_id)
    def acknowledge(self,alert_id:BusinessId,*,acknowledged_at:datetime,acknowledged_by:BusinessId,reason:str):
        record=self.get(alert_id)
        if record.status is not GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus.OPEN: raise ValueError("ERR-KICAD-0319: Nur ein offener Alarm kann bestaetigt werden.")
        instant,normalized=_validate_action(acknowledged_at,reason)
        if instant<record.created_at: raise ValueError("ERR-KICAD-0320: Die Bestaetigung liegt vor der Alarmerzeugung.")
        self._connection.execute(f"UPDATE {self.TABLE} SET status='ACKNOWLEDGED',acknowledged_at=?,acknowledged_by=?,acknowledgement_reason=? WHERE alert_id=?",(instant.isoformat(),str(acknowledged_by),normalized,str(alert_id))); self._connection.commit(); return self.get(alert_id)
    def resolve(self,alert_id:BusinessId,*,resolved_at:datetime,resolved_by:BusinessId,reason:str):
        record=self.get(alert_id)
        if record.status is not GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus.ACKNOWLEDGED: raise ValueError("ERR-KICAD-0321: Nur ein bestaetigter Alarm kann abgeschlossen werden.")
        instant,normalized=_validate_action(resolved_at,reason)
        if record.acknowledged_at is None or instant<record.acknowledged_at: raise ValueError("ERR-KICAD-0322: Der Abschluss liegt vor der Bestaetigung.")
        self._connection.execute(f"UPDATE {self.TABLE} SET status='RESOLVED',resolved_at=?,resolved_by=?,resolution_reason=? WHERE alert_id=?",(instant.isoformat(),str(resolved_by),normalized,str(alert_id))); self._connection.commit(); return self.get(alert_id)
    def get(self,alert_id:BusinessId):
        row=self._connection.execute(f"SELECT * FROM {self.TABLE} WHERE alert_id=?",(str(alert_id),)).fetchone()
        if row is None: raise ValueError("ERR-KICAD-0323: Sicherheitsalarm wurde nicht gefunden.")
        return _decode(row)
    def list_for_status(self,status:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus):
        return tuple(_decode(r) for r in self._connection.execute(f"SELECT * FROM {self.TABLE} WHERE status=? ORDER BY created_at DESC,alert_id DESC",(status.value,)).fetchall())

def _validate_action(at:datetime,reason:str):
    if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0324: Bearbeitungszeitpunkte benoetigen eine Zeitzone.")
    normalized=reason.strip()
    if not normalized: raise ValueError("ERR-KICAD-0325: Die Alarmbearbeitung benoetigt eine Begruendung.")
    return at,normalized

def _decode(row):
    S=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryStatus
    return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord(BusinessId(str(row[0])),Level(str(row[1])),S(str(row[2])),datetime.fromisoformat(str(row[3])),datetime.fromisoformat(str(row[4])),int(row[5]),int(row[6]),int(row[7]),int(row[8]),tuple(json.loads(str(row[9]))),CorrelationId(str(row[10])),datetime.fromisoformat(str(row[11])) if row[11] else None,BusinessId(str(row[12])) if row[12] else None,str(row[13]) if row[13] else None,datetime.fromisoformat(str(row[14])) if row[14] else None,BusinessId(str(row[15])) if row[15] else None,str(row[16]) if row[16] else None)
