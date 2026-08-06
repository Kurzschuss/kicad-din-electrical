"""Autorisierung und Audit der Bearbeitung von Alarmen zu abgelehnten Alarmbearbeitungsversuchen."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_release_alert_attempt_history import GlobalSecurityStaffingReleaseAlertAttemptHistoryRecord, SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACKNOWLEDGE = BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACKNOWLEDGE")
PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_RESOLVE = BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-RESOLVE")

class GlobalSecurityStaffingReleaseAlertAttemptHistoryAction(StrEnum):
    ACKNOWLEDGE="ACKNOWLEDGE"
    RESOLVE="RESOLVE"

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRecord:
    action_id:BusinessId; alert_id:BusinessId; action:GlobalSecurityStaffingReleaseAlertAttemptHistoryAction
    occurred_at:datetime; actor_id:BusinessId; acting_role:BusinessId; permission_id:BusinessId
    responsibility:GlobalSecurityResponsibilityType; reason:str; correlation_id:CorrelationId

@dataclass(frozen=True, slots=True)
class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryAction:
    authority:GlobalSecurityAuthorityResolution; authorization:AuthorizationResult
    alert:GlobalSecurityStaffingReleaseAlertAttemptHistoryRecord
    audit_record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRecord

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRepository:
    def __init__(self, connection:sqlite3.Connection):
        self._connection=connection
        connection.execute("""CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_alert_attempt_action_audit (
        action_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL, occurred_at TEXT NOT NULL,
        actor_id TEXT NOT NULL, acting_role TEXT NOT NULL, permission_id TEXT NOT NULL, responsibility TEXT NOT NULL,
        reason TEXT NOT NULL, correlation_id TEXT NOT NULL)""")
        connection.commit()
    def append(self, record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRecord):
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None: raise ValueError("ERR-KICAD-0215: Der Auditzeitpunkt benötigt eine Zeitzone.")
        reason=record.reason.strip()
        if not reason: raise ValueError("ERR-KICAD-0216: Das Bearbeitungsaudit benötigt eine Begründung.")
        try:
            self._connection.execute("INSERT INTO projectos_global_security_staffing_release_alert_attempt_action_audit VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.action_id),str(record.alert_id),record.action.value,record.occurred_at.astimezone(timezone.utc).isoformat(),str(record.actor_id),str(record.acting_role),str(record.permission_id),record.responsibility.value,reason,str(record.correlation_id)))
            self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0217: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self, alert_id:BusinessId):
        rows=self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alert_attempt_action_audit WHERE alert_id=? ORDER BY occurred_at,action_id",(str(alert_id),)).fetchall()
        return tuple(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRecord(BusinessId(str(r[0])),BusinessId(str(r[1])),GlobalSecurityStaffingReleaseAlertAttemptHistoryAction(str(r[2])),datetime.fromisoformat(str(r[3])),BusinessId(str(r[4])),BusinessId(str(r[5])),BusinessId(str(r[6])),GlobalSecurityResponsibilityType(str(r[7])),str(r[8]),CorrelationId(str(r[9]))) for r in rows)

class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryService:
    def __init__(self, responsibilities:SQLiteGlobalSecurityResponsibilityRepository, identities:SQLiteIdentityRepository, alerts:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryRepository, audit:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRepository, attempt_audit=None):
        self._responsibilities=responsibilities; self._identities=identities; self._alerts=alerts; self._audit=audit; self._attempt_audit=attempt_audit
    def acknowledge(self, alert_id:BusinessId, *, action_id:BusinessId, acknowledged_at:datetime, acting_role:BusinessId, reason:str, correlation_id:CorrelationId, unavailable_user_ids:frozenset[BusinessId]=frozenset(), attempt_id:BusinessId|None=None):
        return self._execute(alert_id,action_id,acknowledged_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACKNOWLEDGE,GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.ACKNOWLEDGE,unavailable_user_ids,attempt_id)
    def resolve(self, alert_id:BusinessId, *, action_id:BusinessId, resolved_at:datetime, acting_role:BusinessId, reason:str, correlation_id:CorrelationId, unavailable_user_ids:frozenset[BusinessId]=frozenset(), attempt_id:BusinessId|None=None):
        return self._execute(alert_id,action_id,resolved_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_RESOLVE,GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.RESOLVE,unavailable_user_ids,attempt_id)
    def _execute(self, alert_id, action_id, at, acting_role, reason, correlation_id, permission, action, unavailable_user_ids, attempt_id):
        if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0213: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
        if self._attempt_audit is not None and attempt_id is None: raise ValueError("ERR-KICAD-0225: Das Versuchsaudit ist aktiviert, aber die Versuchskennung fehlt.")
        instant=at.astimezone(timezone.utc); actor_id=None
        try:
            authority=self._responsibilities.resolve(at=instant,unavailable_user_ids=unavailable_user_ids)
            actor_id=authority.user.user_id
            authorization=self._identities.create_authorization_service().authorize(self._identities.create_context(actor_id),permission,at=instant)
            if not authorization.allowed: raise PermissionError(f"ERR-KICAD-0218: {authorization.reason}")
            if acting_role not in authorization.matched_roles: raise PermissionError("ERR-KICAD-0219: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht.")
        except (LookupError, PermissionError) as exc:
            if self._attempt_audit is not None:
                from .kicad_global_security_release_alert_attempt_action_attempt_audit import GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord
                message=str(exc); code=message.split(":",1)[0].strip() or "ERR-KICAD-0218"
                self._attempt_audit.append(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptRecord(attempt_id,alert_id,action,instant,actor_id,acting_role,permission,code,message,correlation_id))
            raise
        if action is GlobalSecurityStaffingReleaseAlertAttemptHistoryAction.ACKNOWLEDGE:
            alert=self._alerts.acknowledge(alert_id,acknowledged_at=instant,acknowledged_by=authority.user.user_id,reason=reason)
        else:
            alert=self._alerts.resolve(alert_id,resolved_at=instant,resolved_by=authority.user.user_id,reason=reason)
        record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAuditRecord(action_id,alert_id,action,instant,authority.user.user_id,acting_role,permission,authority.source,reason.strip(),correlation_id)
        self._audit.append(record)
        return AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryAction(authority,authorization,alert,record)
