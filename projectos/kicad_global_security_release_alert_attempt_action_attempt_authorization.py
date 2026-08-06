"""Autorisierung und Audit der Bearbeitung persistenter Alarme aus AP-0100."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_release_alert_attempt_action_attempt_history import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRecord, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACKNOWLEDGE")
PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_RESOLVE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-RESOLVE")

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction(StrEnum):
    ACKNOWLEDGE="ACKNOWLEDGE"; RESOLVE="RESOLVE"

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord:
    action_id:BusinessId; alert_id:BusinessId; action:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction
    occurred_at:datetime; actor_id:BusinessId; acting_role:BusinessId; permission_id:BusinessId
    responsibility:GlobalSecurityResponsibilityType; reason:str; correlation_id:CorrelationId

@dataclass(frozen=True,slots=True)
class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction:
    authority:GlobalSecurityAuthorityResolution; authorization:AuthorizationResult
    alert:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRecord
    audit_record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository:
    def __init__(self,connection:sqlite3.Connection):
        self._connection=connection
        connection.execute("""CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_audit (
        action_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL, occurred_at TEXT NOT NULL,
        actor_id TEXT NOT NULL, acting_role TEXT NOT NULL, permission_id TEXT NOT NULL, responsibility TEXT NOT NULL,
        reason TEXT NOT NULL, correlation_id TEXT NOT NULL)"""); connection.commit()
    def append(self,record):
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None: raise ValueError("ERR-KICAD-0252: Der Auditzeitpunkt benötigt eine Zeitzone.")
        reason=record.reason.strip()
        if not reason: raise ValueError("ERR-KICAD-0253: Das Bearbeitungsaudit benötigt eine Begründung.")
        try:
            self._connection.execute("INSERT INTO projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_audit VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.action_id),str(record.alert_id),record.action.value,record.occurred_at.astimezone(timezone.utc).isoformat(),str(record.actor_id),str(record.acting_role),str(record.permission_id),record.responsibility.value,reason,str(record.correlation_id))); self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0254: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self,alert_id):
        rows=self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_audit WHERE alert_id=? ORDER BY occurred_at,action_id",(str(alert_id),)).fetchall()
        return tuple(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord(BusinessId(str(r[0])),BusinessId(str(r[1])),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction(str(r[2])),datetime.fromisoformat(str(r[3])),BusinessId(str(r[4])),BusinessId(str(r[5])),BusinessId(str(r[6])),GlobalSecurityResponsibilityType(str(r[7])),str(r[8]),CorrelationId(str(r[9]))) for r in rows)

class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryService:
    def __init__(self,responsibilities:SQLiteGlobalSecurityResponsibilityRepository,identities:SQLiteIdentityRepository,alerts:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryRepository,audit:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRepository,attempt_audit=None):
        self._responsibilities=responsibilities; self._identities=identities; self._alerts=alerts; self._audit=audit; self._attempt_audit=attempt_audit
    def acknowledge(self,alert_id:BusinessId,*,action_id:BusinessId,acknowledged_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,attempt_id:BusinessId|None=None,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,acknowledged_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE,attempt_id,unavailable_user_ids)
    def resolve(self,alert_id:BusinessId,*,action_id:BusinessId,resolved_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,attempt_id:BusinessId|None=None,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,resolved_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_RESOLVE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.RESOLVE,attempt_id,unavailable_user_ids)
    def _execute(self,alert_id,action_id,at,acting_role,reason,correlation_id,permission,action,attempt_id,unavailable_user_ids):
        if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0250: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
        if self._attempt_audit is not None and attempt_id is None: raise ValueError("ERR-KICAD-0262: Das Versuchsaudit ist aktiviert, aber die Versuchskennung fehlt.")
        instant=at.astimezone(timezone.utc); authority=None
        try:
            authority=self._responsibilities.resolve(at=instant,unavailable_user_ids=unavailable_user_ids)
            authorization=self._identities.create_authorization_service().authorize(self._identities.create_context(authority.user.user_id),permission,at=instant)
            if not authorization.allowed: raise PermissionError(f"ERR-KICAD-0255: {authorization.reason}")
            if acting_role not in authorization.matched_roles: raise PermissionError("ERR-KICAD-0256: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht.")
        except (PermissionError,ValueError) as exc:
            if self._attempt_audit is not None:
                from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord
                text=str(exc); code=text.split(":",1)[0] if ":" in text else "ERR-KICAD-UNKNOWN"
                self._attempt_audit.append(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptRecord(attempt_id,alert_id,action,instant,authority.user.user_id if authority else None,acting_role,permission,code,text,correlation_id))
            raise
        alert=self._alerts.acknowledge(alert_id,acknowledged_at=instant,acknowledged_by=authority.user.user_id,reason=reason) if action is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE else self._alerts.resolve(alert_id,resolved_at=instant,resolved_by=authority.user.user_id,reason=reason)
        record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAuditRecord(action_id,alert_id,action,instant,authority.user.user_id,acting_role,permission,authority.source,reason.strip(),correlation_id); self._audit.append(record)
        return AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryAction(authority,authorization,alert,record)
