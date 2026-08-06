"""Separates Audit abgelehnter Bearbeitungsversuche fuer Alarme aus AP-0110."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord:
    attempt_id:BusinessId; alert_id:BusinessId; action:Action; attempted_at:datetime
    actor_id:BusinessId|None; acting_role:BusinessId; permission_id:BusinessId
    denial_code:str; denial_reason:str; correlation_id:CorrelationId

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRepository:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_alert_action_attempt_audit"
    def __init__(self,connection:sqlite3.Connection):
        self._connection=connection
        connection.execute(f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (attempt_id TEXT PRIMARY KEY,alert_id TEXT NOT NULL,action TEXT NOT NULL,attempted_at TEXT NOT NULL,actor_id TEXT,acting_role TEXT NOT NULL,permission_id TEXT NOT NULL,denial_code TEXT NOT NULL,denial_reason TEXT NOT NULL,correlation_id TEXT NOT NULL)""")
        connection.commit()
    def append(self,record):
        if record.attempted_at.tzinfo is None or record.attempted_at.utcoffset() is None: raise ValueError("ERR-KICAD-0331: Der Versuchszeitpunkt benoetigt eine Zeitzone.")
        code=record.denial_code.strip(); reason=record.denial_reason.strip()
        if not code: raise ValueError("ERR-KICAD-0332: Der Ablehnungscode fehlt.")
        if not reason: raise ValueError("ERR-KICAD-0333: Die Ablehnungsbegruendung fehlt.")
        try:
            self._connection.execute(f"INSERT INTO {self.TABLE} VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.attempt_id),str(record.alert_id),record.action.value,record.attempted_at.astimezone(timezone.utc).isoformat(),str(record.actor_id) if record.actor_id else None,str(record.acting_role),str(record.permission_id),code,reason,str(record.correlation_id))); self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0334: Die Versuchskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self,alert_id):
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE} WHERE alert_id=? ORDER BY attempted_at,attempt_id",(str(alert_id),)).fetchall()
        R=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord
        return tuple(R(BusinessId(r[0]),BusinessId(r[1]),Action(r[2]),datetime.fromisoformat(r[3]),BusinessId(r[4]) if r[4] else None,BusinessId(r[5]),BusinessId(r[6]),r[7],r[8],CorrelationId(r[9])) for r in rows)
