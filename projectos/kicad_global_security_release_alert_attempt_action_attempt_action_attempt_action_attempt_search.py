"""Suche und Sicherheitsdiagnose fuer abgelehnte Bearbeitungsversuche aus AP-0107."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import math, sqlite3
from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction as Action
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter:
    alert_id:BusinessId|None=None; action:Action|None=None; actor_id:BusinessId|None=None
    acting_role:BusinessId|None=None; permission_id:BusinessId|None=None; denial_code:str|None=None
    correlation_id:CorrelationId|None=None; free_text:str|None=None; from_at:datetime|None=None; to_at:datetime|None=None
    def __post_init__(self):
        for value in (self.from_at,self.to_at):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None): raise ValueError("ERR-KICAD-0300: Zeitfilter benoetigen eine Zeitzone.")
        if self.from_at is not None and self.to_at is not None and self.from_at>self.to_at: raise ValueError("ERR-KICAD-0301: Der Beginn liegt nach dem Ende.")

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchPage:
    items:tuple[Record,...]; page:int; page_size:int; total_items:int; total_pages:int
    @property
    def has_previous(self): return self.page>1
    @property
    def has_next(self): return self.page<self.total_pages

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptDiagnostic:
    total_attempts:int; affected_alerts:int; distinct_actors:int; attempts_without_actor:int; distinct_roles:int
    acknowledge_attempts:int; resolve_attempts:int; first_attempt_at:datetime|None; last_attempt_at:datetime|None
    top_denial_codes:tuple[tuple[str,int],...]; top_permissions:tuple[tuple[str,int],...]; top_roles:tuple[tuple[str,int],...]

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchService:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_audit"
    def __init__(self,connection:sqlite3.Connection): self._connection=connection
    def search(self,filter:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter|None=None,*,page:int=1,page_size:int=50):
        if page<1: raise ValueError("ERR-KICAD-0302: Die Seitennummer muss mindestens 1 sein.")
        if page_size<1 or page_size>200: raise ValueError("ERR-KICAD-0303: Die Seitengroesse muss zwischen 1 und 200 liegen.")
        where,args=self._where(filter or GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter())
        total=int(self._connection.execute(f"SELECT COUNT(*) FROM {self.TABLE}{where}",args).fetchone()[0]); total_pages=math.ceil(total/page_size) if total else 0
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE}{where} ORDER BY attempted_at DESC,attempt_id DESC LIMIT ? OFFSET ?",(*args,page_size,(page-1)*page_size)).fetchall()
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchPage(tuple(self._decode(r) for r in rows),page,page_size,total,total_pages)
    def diagnose(self,filter:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter|None=None):
        where,args=self._where(filter or GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptSearchFilter())
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE}{where} ORDER BY attempted_at",args).fetchall(); records=tuple(self._decode(r) for r in rows)
        actions=Counter(r.action.value for r in records); codes=Counter(r.denial_code for r in records); perms=Counter(str(r.permission_id) for r in records); roles=Counter(str(r.acting_role) for r in records)
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptDiagnostic(len(records),len({r.alert_id for r in records}),len({r.actor_id for r in records if r.actor_id}),sum(r.actor_id is None for r in records),len({r.acting_role for r in records}),actions[Action.ACKNOWLEDGE.value],actions[Action.RESOLVE.value],records[0].attempted_at if records else None,records[-1].attempted_at if records else None,tuple(codes.most_common(10)),tuple(perms.most_common(10)),tuple(roles.most_common(10)))
    def _where(self,f):
        clauses=[]; args=[]
        for column,value in (("alert_id",f.alert_id),("action",f.action.value if f.action else None),("actor_id",f.actor_id),("acting_role",f.acting_role),("permission_id",f.permission_id),("denial_code",f.denial_code),("correlation_id",f.correlation_id)):
            if value is not None: clauses.append(f"{column}=?"); args.append(str(value))
        if f.free_text and f.free_text.strip(): clauses.append("LOWER(denial_reason) LIKE ?"); args.append(f"%{f.free_text.strip().lower()}%")
        if f.from_at is not None: clauses.append("attempted_at>=?"); args.append(f.from_at.astimezone(timezone.utc).isoformat())
        if f.to_at is not None: clauses.append("attempted_at<=?"); args.append(f.to_at.astimezone(timezone.utc).isoformat())
        return (" WHERE "+" AND ".join(clauses) if clauses else ""),tuple(args)
    @staticmethod
    def _decode(r):
        return Record(BusinessId(str(r[0])),BusinessId(str(r[1])),Action(str(r[2])),datetime.fromisoformat(str(r[3])),BusinessId(str(r[4])) if r[4] else None,BusinessId(str(r[5])),BusinessId(str(r[6])),str(r[7]),str(r[8]),CorrelationId(str(r[9])))
