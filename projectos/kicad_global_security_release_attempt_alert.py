"""Konfigurierbare Alarmbewertung abgelehnter globaler Besetzungsfreigabeversuche."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import sqlite3
from .identifiers import BusinessId

class GlobalSecurityStaffingReleaseAlertLevel(StrEnum):
    CLEAR="CLEAR"; WARNING="WARNING"; CRITICAL="CRITICAL"

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAttemptAlertPolicy:
    window: timedelta = timedelta(hours=24)
    warning_attempts: int = 3
    critical_attempts: int = 5
    warning_per_actor: int | None = 3
    critical_per_actor: int | None = 5
    warning_per_role: int | None = None
    critical_per_role: int | None = None
    warning_without_actor: int | None = 1
    critical_without_actor: int | None = 3
    critical_denial_codes: tuple[str, ...] = ()
    def __post_init__(self):
        if self.window <= timedelta(0): raise ValueError("ERR-KICAD-0158: Das Alarmzeitfenster muss größer als null sein.")
        if self.warning_attempts < 1 or self.critical_attempts < self.warning_attempts: raise ValueError("ERR-KICAD-0159: Ungültige Gesamtversuchsschwellen.")
        for w,c in ((self.warning_per_actor,self.critical_per_actor),(self.warning_per_role,self.critical_per_role),(self.warning_without_actor,self.critical_without_actor)):
            if (w is not None and w < 1) or (c is not None and c < 1): raise ValueError("ERR-KICAD-0160: Optionale Schwellen müssen mindestens 1 sein.")
            if w is not None and c is not None and c < w: raise ValueError("ERR-KICAD-0161: Kritische Schwellen dürfen nicht unter Warnschwellen liegen.")
        object.__setattr__(self,"critical_denial_codes",tuple(dict.fromkeys(x.strip().upper() for x in self.critical_denial_codes if x.strip())))

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertFinding:
    code: str; level: GlobalSecurityStaffingReleaseAlertLevel; message: str; subject_id: BusinessId | None = None

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAttemptAlertResult:
    evaluated_at: datetime; window_start: datetime; total_attempts: int; attempts_without_actor: int
    level: GlobalSecurityStaffingReleaseAlertLevel; findings: tuple[GlobalSecurityStaffingReleaseAlertFinding,...]
    @property
    def alert(self): return self.level is not GlobalSecurityStaffingReleaseAlertLevel.CLEAR

class GlobalSecurityStaffingReleaseAttemptAlertService:
    def __init__(self, connection: sqlite3.Connection): self._connection=connection
    def evaluate(self, *, evaluated_at: datetime, policy: GlobalSecurityStaffingReleaseAttemptAlertPolicy | None=None):
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None: raise ValueError("ERR-KICAD-0162: Der Bewertungszeitpunkt benötigt eine Zeitzone.")
        policy=policy or GlobalSecurityStaffingReleaseAttemptAlertPolicy(); end=evaluated_at.astimezone(timezone.utc); start=end-policy.window
        rows=self._connection.execute("SELECT actor_id,acting_role,denial_code FROM projectos_global_security_staffing_release_attempt_audit WHERE attempted_at>=? AND attempted_at<=?",(start.isoformat(),end.isoformat())).fetchall()
        actors=Counter(str(r[0]) for r in rows if r[0]); roles=Counter(str(r[1]) for r in rows); codes={str(r[2]) for r in rows}; no_actor=sum(r[0] is None for r in rows); findings=[]
        self._threshold(findings,len(rows),policy.warning_attempts,policy.critical_attempts,"WARN-KICAD-0005","ERR-KICAD-0163","abgelehnte globale Besetzungsfreigabeversuche")
        for sid,count in actors.items(): self._subject(findings,count,policy.warning_per_actor,policy.critical_per_actor,"WARN-KICAD-0006","ERR-KICAD-0164","Benutzer",BusinessId(sid))
        for sid,count in roles.items(): self._subject(findings,count,policy.warning_per_role,policy.critical_per_role,"WARN-KICAD-0007","ERR-KICAD-0165","Rolle",BusinessId(sid))
        self._threshold(findings,no_actor,policy.warning_without_actor,policy.critical_without_actor,"WARN-KICAD-0008","ERR-KICAD-0166","Versuche ohne ermittelte Person")
        for code in sorted(codes.intersection(policy.critical_denial_codes)): findings.append(GlobalSecurityStaffingReleaseAlertFinding("ERR-KICAD-0167",GlobalSecurityStaffingReleaseAlertLevel.CRITICAL,f"Kritischer Ablehnungscode beobachtet: {code}."))
        level=GlobalSecurityStaffingReleaseAlertLevel.CRITICAL if any(x.level is GlobalSecurityStaffingReleaseAlertLevel.CRITICAL for x in findings) else (GlobalSecurityStaffingReleaseAlertLevel.WARNING if findings else GlobalSecurityStaffingReleaseAlertLevel.CLEAR)
        return GlobalSecurityStaffingReleaseAttemptAlertResult(end,start,len(rows),no_actor,level,tuple(sorted(findings,key=lambda x:(x.level.value,x.code,str(x.subject_id or '')))))
    @staticmethod
    def _threshold(out,count,w,c,wcode,ccode,label):
        if c is not None and count>=c: out.append(GlobalSecurityStaffingReleaseAlertFinding(ccode,GlobalSecurityStaffingReleaseAlertLevel.CRITICAL,f"{count} {label}; kritische Schwelle: {c}."))
        elif w is not None and count>=w: out.append(GlobalSecurityStaffingReleaseAlertFinding(wcode,GlobalSecurityStaffingReleaseAlertLevel.WARNING,f"{count} {label}; Warnschwelle: {w}."))
    @staticmethod
    def _subject(out,count,w,c,wcode,ccode,label,sid):
        if c is not None and count>=c: out.append(GlobalSecurityStaffingReleaseAlertFinding(ccode,GlobalSecurityStaffingReleaseAlertLevel.CRITICAL,f"{count} Versuche für {label} {sid}; kritische Schwelle: {c}.",sid))
        elif w is not None and count>=w: out.append(GlobalSecurityStaffingReleaseAlertFinding(wcode,GlobalSecurityStaffingReleaseAlertLevel.WARNING,f"{count} Versuche für {label} {sid}; Warnschwelle: {w}.",sid))
