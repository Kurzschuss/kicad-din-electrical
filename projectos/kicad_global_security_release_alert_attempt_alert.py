"""Konfigurierbare Alarmbewertung abgelehnter Bearbeitungsversuche globaler Besetzungsfreigabealarme."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import sqlite3
from .identifiers import BusinessId
from .kicad_global_security_release_alert_authorization import GlobalSecurityStaffingReleaseAlertAction

class GlobalSecurityStaffingReleaseAlertAttemptAlertLevel(StrEnum):
    CLEAR="CLEAR"; WARNING="WARNING"; CRITICAL="CRITICAL"

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy:
    window: timedelta = timedelta(hours=24)
    warning_attempts: int = 3
    critical_attempts: int = 5
    warning_per_actor: int|None = 3
    critical_per_actor: int|None = 5
    warning_per_role: int|None = None
    critical_per_role: int|None = None
    warning_acknowledge: int|None = None
    critical_acknowledge: int|None = None
    warning_resolve: int|None = None
    critical_resolve: int|None = None
    warning_without_actor: int|None = 1
    critical_without_actor: int|None = 3
    critical_denial_codes: tuple[str,...] = ()
    def __post_init__(self):
        if self.window <= timedelta(0): raise ValueError("ERR-KICAD-0193: Das Alarmzeitfenster muss größer als null sein.")
        if self.warning_attempts < 1 or self.critical_attempts < self.warning_attempts: raise ValueError("ERR-KICAD-0194: Ungültige Gesamtversuchsschwellen.")
        for warning,critical in ((self.warning_per_actor,self.critical_per_actor),(self.warning_per_role,self.critical_per_role),(self.warning_acknowledge,self.critical_acknowledge),(self.warning_resolve,self.critical_resolve),(self.warning_without_actor,self.critical_without_actor)):
            if (warning is not None and warning < 1) or (critical is not None and critical < 1): raise ValueError("ERR-KICAD-0195: Optionale Schwellen müssen mindestens 1 sein.")
            if warning is not None and critical is not None and critical < warning: raise ValueError("ERR-KICAD-0196: Kritische Schwellen dürfen nicht unter Warnschwellen liegen.")
        object.__setattr__(self,"critical_denial_codes",tuple(dict.fromkeys(x.strip().upper() for x in self.critical_denial_codes if x.strip())))

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptAlertFinding:
    code:str; level:GlobalSecurityStaffingReleaseAlertAttemptAlertLevel; message:str; subject_id:BusinessId|None=None

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptAlertResult:
    evaluated_at:datetime; window_start:datetime; total_attempts:int; acknowledge_attempts:int; resolve_attempts:int; attempts_without_actor:int
    level:GlobalSecurityStaffingReleaseAlertAttemptAlertLevel; findings:tuple[GlobalSecurityStaffingReleaseAlertAttemptAlertFinding,...]
    @property
    def alert(self): return self.level is not GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CLEAR

class GlobalSecurityStaffingReleaseAlertAttemptAlertService:
    def __init__(self, connection:sqlite3.Connection): self._connection=connection
    def evaluate(self, *, evaluated_at:datetime, policy:GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy|None=None):
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None: raise ValueError("ERR-KICAD-0197: Der Bewertungszeitpunkt benötigt eine Zeitzone.")
        policy=policy or GlobalSecurityStaffingReleaseAlertAttemptAlertPolicy(); end=evaluated_at.astimezone(timezone.utc); start=end-policy.window
        rows=self._connection.execute("SELECT action,actor_id,acting_role,denial_code FROM projectos_global_security_staffing_release_alert_action_attempt_audit WHERE attempted_at>=? AND attempted_at<=?",(start.isoformat(),end.isoformat())).fetchall()
        actions=Counter(str(r[0]) for r in rows); actors=Counter(str(r[1]) for r in rows if r[1]); roles=Counter(str(r[2]) for r in rows); codes={str(r[3]) for r in rows}; without_actor=sum(r[1] is None for r in rows); findings=[]
        self._threshold(findings,len(rows),policy.warning_attempts,policy.critical_attempts,"WARN-KICAD-0009","ERR-KICAD-0198","abgelehnte Alarmbearbeitungsversuche")
        for sid,count in actors.items(): self._subject(findings,count,policy.warning_per_actor,policy.critical_per_actor,"WARN-KICAD-0010","ERR-KICAD-0199","Benutzer",BusinessId(sid))
        for sid,count in roles.items(): self._subject(findings,count,policy.warning_per_role,policy.critical_per_role,"WARN-KICAD-0011","ERR-KICAD-0200","Rolle",BusinessId(sid))
        self._threshold(findings,actions[GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE.value],policy.warning_acknowledge,policy.critical_acknowledge,"WARN-KICAD-0012","ERR-KICAD-0201","abgelehnte Bestätigungsversuche")
        self._threshold(findings,actions[GlobalSecurityStaffingReleaseAlertAction.RESOLVE.value],policy.warning_resolve,policy.critical_resolve,"WARN-KICAD-0013","ERR-KICAD-0202","abgelehnte Abschlussversuche")
        self._threshold(findings,without_actor,policy.warning_without_actor,policy.critical_without_actor,"WARN-KICAD-0014","ERR-KICAD-0203","Versuche ohne ermittelte Person")
        for code in sorted(codes.intersection(policy.critical_denial_codes)): findings.append(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding("ERR-KICAD-0204",GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL,f"Kritischer Ablehnungscode beobachtet: {code}."))
        level=GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL if any(x.level is GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL for x in findings) else (GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING if findings else GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CLEAR)
        ordered=tuple(sorted(findings,key=lambda x:(x.level.value,x.code,str(x.subject_id or ''),x.message)))
        return GlobalSecurityStaffingReleaseAlertAttemptAlertResult(end,start,len(rows),actions[GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE.value],actions[GlobalSecurityStaffingReleaseAlertAction.RESOLVE.value],without_actor,level,ordered)
    @staticmethod
    def _threshold(out,count,warning,critical,warning_code,critical_code,label):
        if critical is not None and count>=critical: out.append(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding(critical_code,GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL,f"{count} {label}; kritische Schwelle: {critical}."))
        elif warning is not None and count>=warning: out.append(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding(warning_code,GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING,f"{count} {label}; Warnschwelle: {warning}."))
    @staticmethod
    def _subject(out,count,warning,critical,warning_code,critical_code,label,subject_id):
        if critical is not None and count>=critical: out.append(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding(critical_code,GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.CRITICAL,f"{count} Versuche für {label} {subject_id}; kritische Schwelle: {critical}.",subject_id))
        elif warning is not None and count>=warning: out.append(GlobalSecurityStaffingReleaseAlertAttemptAlertFinding(warning_code,GlobalSecurityStaffingReleaseAlertAttemptAlertLevel.WARNING,f"{count} Versuche für {label} {subject_id}; Warnschwelle: {warning}.",subject_id))
