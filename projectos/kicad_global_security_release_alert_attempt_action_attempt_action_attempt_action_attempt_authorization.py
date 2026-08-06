"""Autorisierung und unveraenderliches Bearbeitungsaudit fuer Alarme aus AP-0110."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_history import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository,
)

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-ACKNOWLEDGE")
PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-RESOLVE")

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction(StrEnum):
    ACKNOWLEDGE="ACKNOWLEDGE"
    RESOLVE="RESOLVE"

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord:
    action_id:BusinessId; alert_id:BusinessId; action:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction
    occurred_at:datetime; actor_id:BusinessId; acting_role:BusinessId; permission_id:BusinessId
    responsibility:GlobalSecurityResponsibilityType; reason:str; correlation_id:CorrelationId

@dataclass(frozen=True,slots=True)
class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction:
    authority:GlobalSecurityAuthorityResolution; authorization:AuthorizationResult
    alert:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord
    audit_record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_alert_action_audit"
    def __init__(self,connection:sqlite3.Connection):
        self._connection=connection
        connection.execute(f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (action_id TEXT PRIMARY KEY,alert_id TEXT NOT NULL,action TEXT NOT NULL,occurred_at TEXT NOT NULL,actor_id TEXT NOT NULL,acting_role TEXT NOT NULL,permission_id TEXT NOT NULL,responsibility TEXT NOT NULL,reason TEXT NOT NULL,correlation_id TEXT NOT NULL)"""); connection.commit()
    def append(self,record):
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None: raise ValueError("ERR-KICAD-0326: Der Auditzeitpunkt benoetigt eine Zeitzone.")
        reason=record.reason.strip()
        if not reason: raise ValueError("ERR-KICAD-0327: Das Bearbeitungsaudit benoetigt eine Begruendung.")
        try:
            self._connection.execute(f"INSERT INTO {self.TABLE} VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.action_id),str(record.alert_id),record.action.value,record.occurred_at.astimezone(timezone.utc).isoformat(),str(record.actor_id),str(record.acting_role),str(record.permission_id),record.responsibility.value,reason,str(record.correlation_id))); self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0328: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self,alert_id):
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE} WHERE alert_id=? ORDER BY occurred_at,action_id",(str(alert_id),)).fetchall(); A=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction; R=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord
        return tuple(R(BusinessId(r[0]),BusinessId(r[1]),A(r[2]),datetime.fromisoformat(r[3]),BusinessId(r[4]),BusinessId(r[5]),BusinessId(r[6]),GlobalSecurityResponsibilityType(r[7]),r[8],CorrelationId(r[9])) for r in rows)

class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryService:
    def __init__(self,responsibilities:SQLiteGlobalSecurityResponsibilityRepository,identities:SQLiteIdentityRepository,alerts:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository,audit:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository,attempt_audit=None):
        self._responsibilities=responsibilities; self._identities=identities; self._alerts=alerts; self._audit=audit; self._attempt_audit=attempt_audit
    def acknowledge(self,alert_id:BusinessId,*,action_id:BusinessId,acknowledged_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,attempt_id:BusinessId|None=None,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,attempt_id,acknowledged_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE,unavailable_user_ids)
    def resolve(self,alert_id:BusinessId,*,action_id:BusinessId,resolved_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,attempt_id:BusinessId|None=None,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,attempt_id,resolved_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.RESOLVE,unavailable_user_ids)
    def _execute(self,alert_id,action_id,attempt_id,at,acting_role,reason,correlation_id,permission,action,unavailable_user_ids):
        if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0324: Bearbeitungszeitpunkte benoetigen eine Zeitzone.")
        if self._attempt_audit is not None and attempt_id is None: raise ValueError("ERR-KICAD-0335: Das Versuchsaudit ist aktiviert, aber die Versuchskennung fehlt.")
        instant=at.astimezone(timezone.utc); actor_id=None
        try:
            authority=self._responsibilities.resolve(at=instant,unavailable_user_ids=unavailable_user_ids); actor_id=authority.user.user_id
            authorization=self._identities.create_authorization_service().authorize(self._identities.create_context(actor_id),permission,at=instant)
            if not authorization.allowed: raise PermissionError(f"ERR-KICAD-0329: {authorization.reason}")
            if acting_role not in authorization.matched_roles: raise PermissionError("ERR-KICAD-0330: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht.")
        except Exception as exc:
            self._append_denial(attempt_id,alert_id,action,instant,actor_id,acting_role,permission,exc,correlation_id)
            raise
        alert=self._alerts.acknowledge(alert_id,acknowledged_at=instant,acknowledged_by=actor_id,reason=reason) if action is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE else self._alerts.resolve(alert_id,resolved_at=instant,resolved_by=actor_id,reason=reason)
        record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord(action_id,alert_id,action,instant,actor_id,acting_role,permission,authority.source,reason.strip(),correlation_id); self._audit.append(record)
        return AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction(authority,authorization,alert,record)
    def _append_denial(self,attempt_id,alert_id,action,instant,actor_id,acting_role,permission,exc,correlation_id):
        if self._attempt_audit is None: return
        from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAttemptRecord as Record
        text=str(exc).strip() or exc.__class__.__name__; code=text.split(":",1)[0] if ":" in text else exc.__class__.__name__.upper()
        self._attempt_audit.append(Record(attempt_id,alert_id,action,instant,actor_id,acting_role,permission,code,text,correlation_id))
