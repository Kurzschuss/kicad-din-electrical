"""Alarmbewertung fuer abgelehnte Bearbeitungsversuche aus AP-0102."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import sqlite3
from .identifiers import BusinessId
from .kicad_global_security_release_alert_attempt_action_attempt_authorization import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction as Action

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel(StrEnum):
    CLEAR="CLEAR"; WARNING="WARNING"; CRITICAL="CRITICAL"

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertPolicy:
    window:timedelta=timedelta(hours=24)
    warning_attempts:int=3; critical_attempts:int=5
    warning_per_actor:int|None=3; critical_per_actor:int|None=5
    warning_per_role:int|None=None; critical_per_role:int|None=None
    warning_acknowledge:int|None=None; critical_acknowledge:int|None=None
    warning_resolve:int|None=None; critical_resolve:int|None=None
    warning_without_actor:int|None=1; critical_without_actor:int|None=3
    critical_denial_codes:tuple[str,...]=()
    def __post_init__(self):
        if self.window<=timedelta(0): raise ValueError("ERR-KICAD-0267: Ungueltiges Alarmzeitfenster.")
        if self.warning_attempts<1 or self.critical_attempts<self.warning_attempts: raise ValueError("ERR-KICAD-0268: Ungueltige Gesamtversuchsschwellen.")
        pairs=((self.warning_per_actor,self.critical_per_actor),(self.warning_per_role,self.critical_per_role),(self.warning_acknowledge,self.critical_acknowledge),(self.warning_resolve,self.critical_resolve),(self.warning_without_actor,self.critical_without_actor))
        for warning,critical in pairs:
            if (warning is not None and warning<1) or (critical is not None and critical<1): raise ValueError("ERR-KICAD-0269: Optionale Schwellen muessen mindestens 1 sein.")
            if warning is not None and critical is not None and critical<warning: raise ValueError("ERR-KICAD-0270: Kritische Schwelle liegt unter Warnschwelle.")
        object.__setattr__(self,"critical_denial_codes",tuple(dict.fromkeys(x.strip().upper() for x in self.critical_denial_codes if x.strip())))

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding:
    code:str; level:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel; message:str; subject_id:BusinessId|None=None

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertResult:
    evaluated_at:datetime; window_start:datetime; total_attempts:int; acknowledge_attempts:int; resolve_attempts:int; attempts_without_actor:int
    level:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel
    findings:tuple[GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding,...]
    @property
    def alert(self): return self.level is not GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.CLEAR

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertService:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_audit"
    def __init__(self,connection:sqlite3.Connection): self._connection=connection
    def evaluate(self,*,evaluated_at:datetime,policy:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertPolicy|None=None):
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None: raise ValueError("ERR-KICAD-0271: Bewertungszeitpunkt besitzt keine Zeitzone.")
        policy=policy or GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertPolicy(); end=evaluated_at.astimezone(timezone.utc); start=end-policy.window
        rows=self._connection.execute(f"SELECT action,actor_id,acting_role,denial_code FROM {self.TABLE} WHERE attempted_at>=? AND attempted_at<=?",(start.isoformat(),end.isoformat())).fetchall()
        actions=Counter(str(r[0]) for r in rows); actors=Counter(str(r[1]) for r in rows if r[1]); roles=Counter(str(r[2]) for r in rows); without_actor=sum(r[1] is None for r in rows); codes={str(r[3]).upper() for r in rows}; findings=[]
        self._threshold(findings,len(rows),policy.warning_attempts,policy.critical_attempts,"WARN-KICAD-0021","ERR-KICAD-0272","Gesamtzahl")
        for sid,count in actors.items(): self._subject(findings,count,policy.warning_per_actor,policy.critical_per_actor,"WARN-KICAD-0022","ERR-KICAD-0273","Benutzer",BusinessId(sid))
        for sid,count in roles.items(): self._subject(findings,count,policy.warning_per_role,policy.critical_per_role,"WARN-KICAD-0023","ERR-KICAD-0274","Rolle",BusinessId(sid))
        self._threshold(findings,actions[Action.ACKNOWLEDGE.value],policy.warning_acknowledge,policy.critical_acknowledge,"WARN-KICAD-0024","ERR-KICAD-0275","Bestaetigungsversuche")
        self._threshold(findings,actions[Action.RESOLVE.value],policy.warning_resolve,policy.critical_resolve,"WARN-KICAD-0025","ERR-KICAD-0276","Abschlussversuche")
        self._threshold(findings,without_actor,policy.warning_without_actor,policy.critical_without_actor,"WARN-KICAD-0026","ERR-KICAD-0277","Versuche ohne Person")
        for code in sorted(codes.intersection(policy.critical_denial_codes)): findings.append(self._finding("ERR-KICAD-0278",True,f"Kritischer Ablehnungscode: {code}."))
        critical=any(x.level is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.CRITICAL for x in findings)
        level=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.CRITICAL if critical else (GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.WARNING if findings else GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.CLEAR)
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertResult(end,start,len(rows),actions[Action.ACKNOWLEDGE.value],actions[Action.RESOLVE.value],without_actor,level,tuple(sorted(findings,key=lambda x:(x.level.value,x.code,str(x.subject_id or '')))))
    @classmethod
    def _finding(cls,code,critical,message,subject_id=None):
        level=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.CRITICAL if critical else GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertLevel.WARNING
        return GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptAlertFinding(code,level,message,subject_id)
    @classmethod
    def _threshold(cls,out,count,warning,critical,wcode,ccode,label):
        if critical is not None and count>=critical: out.append(cls._finding(ccode,True,f"{label}: {count}; kritische Schwelle: {critical}."))
        elif warning is not None and count>=warning: out.append(cls._finding(wcode,False,f"{label}: {count}; Warnschwelle: {warning}."))
    @classmethod
    def _subject(cls,out,count,warning,critical,wcode,ccode,label,subject_id):
        if critical is not None and count>=critical: out.append(cls._finding(ccode,True,f"{label} {subject_id}: {count}.",subject_id))
        elif warning is not None and count>=warning: out.append(cls._finding(wcode,False,f"{label} {subject_id}: {count}.",subject_id))
