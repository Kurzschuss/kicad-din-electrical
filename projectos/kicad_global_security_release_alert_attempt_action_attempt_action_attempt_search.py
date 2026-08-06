"""Suche und Sicherheitsdiagnose abgelehnter Bearbeitungsversuche aus AP-0102."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import math, sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_alert_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter:
    alert_id:BusinessId|None=None
    action:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction|None=None
    actor_id:BusinessId|None=None
    acting_role:BusinessId|None=None
    permission_id:BusinessId|None=None
    denial_code:str|None=None
    correlation_id:CorrelationId|None=None
    reason_text:str|None=None
    from_timestamp:datetime|None=None
    until_timestamp:datetime|None=None
    def __post_init__(self):
        for value in (self.from_timestamp,self.until_timestamp):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("ERR-KICAD-0263: Zeitfilter benötigen einen Zeitzonenbezug.")
        if self.from_timestamp and self.until_timestamp and self.from_timestamp>self.until_timestamp:
            raise ValueError("ERR-KICAD-0264: Der Beginn liegt nach dem Ende des Zeitraums.")

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchPage:
    items:tuple[GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord,...]
    page:int; page_size:int; total_items:int; total_pages:int
    @property
    def has_previous(self): return self.page>1
    @property
    def has_next(self): return self.page<self.total_pages

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptDiagnostic:
    total_attempts:int; distinct_alerts:int; distinct_actors:int; attempts_without_actor:int; distinct_roles:int
    acknowledge_attempts:int; resolve_attempts:int; first_attempt_at:datetime|None; latest_attempt_at:datetime|None
    top_denial_codes:tuple[tuple[str,int],...]; top_permissions:tuple[tuple[str,int],...]; top_roles:tuple[tuple[str,int],...]

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchService:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_audit"
    def __init__(self,connection:sqlite3.Connection): self._connection=connection
    def search(self,filters:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter|None=None,*,page:int=1,page_size:int=50):
        if page<1: raise ValueError("ERR-KICAD-0265: Die Seitennummer muss mindestens 1 sein.")
        if page_size<1 or page_size>200: raise ValueError("ERR-KICAD-0266: Die Seitengröße muss zwischen 1 und 200 liegen.")
        f=filters or GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter(); where,params=self._where(f)
        total=int(self._connection.execute(f"SELECT COUNT(*) FROM {self.TABLE} {where}",params).fetchone()[0])
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE} {where} ORDER BY attempted_at DESC,attempt_id DESC LIMIT ? OFFSET ?",(*params,page_size,(page-1)*page_size)).fetchall()
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchPage(tuple(_decode(r) for r in rows),page,page_size,total,math.ceil(total/page_size) if total else 0)
    def diagnostic(self,filters:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter|None=None):
        f=filters or GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter(); where,params=self._where(f)
        records=tuple(_decode(r) for r in self._connection.execute(f"SELECT * FROM {self.TABLE} {where} ORDER BY attempted_at",params).fetchall())
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptDiagnostic(
            len(records),len({r.alert_id for r in records}),len({r.actor_id for r in records if r.actor_id}),sum(r.actor_id is None for r in records),len({r.acting_role for r in records}),
            sum(r.action is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE for r in records),
            sum(r.action is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.RESOLVE for r in records),
            records[0].attempted_at if records else None,records[-1].attempted_at if records else None,
            tuple(Counter(r.denial_code for r in records).most_common(10)),tuple(Counter(str(r.permission_id) for r in records).most_common(10)),tuple(Counter(str(r.acting_role) for r in records).most_common(10)))
    @staticmethod
    def _where(f):
        clauses=[]; params=[]
        for column,value in (("alert_id",f.alert_id),("actor_id",f.actor_id),("acting_role",f.acting_role),("permission_id",f.permission_id),("correlation_id",f.correlation_id)):
            if value is not None: clauses.append(f"{column}=?"); params.append(str(value))
        if f.action is not None: clauses.append("action=?"); params.append(f.action.value)
        if f.denial_code: clauses.append("denial_code=?"); params.append(f.denial_code.strip().upper())
        if f.reason_text: clauses.append("LOWER(denial_reason) LIKE ?"); params.append(f"%{f.reason_text.strip().lower()}%")
        if f.from_timestamp: clauses.append("attempted_at>=?"); params.append(f.from_timestamp.astimezone(timezone.utc).isoformat())
        if f.until_timestamp: clauses.append("attempted_at<=?"); params.append(f.until_timestamp.astimezone(timezone.utc).isoformat())
        return ("WHERE "+" AND ".join(clauses) if clauses else "",tuple(params))

def _decode(row):
    return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord(
        BusinessId(str(row[0])),BusinessId(str(row[1])),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction(str(row[2])),datetime.fromisoformat(str(row[3])),
        BusinessId(str(row[4])) if row[4] else None,BusinessId(str(row[5])),BusinessId(str(row[6])),str(row[7]),str(row[8]),CorrelationId(str(row[9])))
