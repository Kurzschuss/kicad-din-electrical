"""Autorisierung und unveraenderliches Bearbeitungsaudit fuer Alarme aus AP-0105."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_release_alert_attempt_action_attempt_action_attempt_history import (
    GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord,
    SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository,
)

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-ACKNOWLEDGE")
PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE=BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-RESOLVE")

class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction(StrEnum):
    ACKNOWLEDGE="ACKNOWLEDGE"
    RESOLVE="RESOLVE"

@dataclass(frozen=True,slots=True)
class GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord:
    action_id:BusinessId
    alert_id:BusinessId
    action:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction
    occurred_at:datetime
    actor_id:BusinessId
    acting_role:BusinessId
    permission_id:BusinessId
    responsibility:GlobalSecurityResponsibilityType
    reason:str
    correlation_id:CorrelationId

@dataclass(frozen=True,slots=True)
class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction:
    authority:GlobalSecurityAuthorityResolution
    authorization:AuthorizationResult
    alert:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRecord
    audit_record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord

class SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository:
    TABLE="projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_audit"
    def __init__(self,connection:sqlite3.Connection):
        self._connection=connection
        connection.execute(f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
        action_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL, occurred_at TEXT NOT NULL,
        actor_id TEXT NOT NULL, acting_role TEXT NOT NULL, permission_id TEXT NOT NULL, responsibility TEXT NOT NULL,
        reason TEXT NOT NULL, correlation_id TEXT NOT NULL)""")
        connection.commit()
    def append(self,record:GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord):
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0289: Der Auditzeitpunkt benoetigt eine Zeitzone.")
        reason=record.reason.strip()
        if not reason:
            raise ValueError("ERR-KICAD-0290: Das Bearbeitungsaudit benoetigt eine Begruendung.")
        try:
            self._connection.execute(f"INSERT INTO {self.TABLE} VALUES (?,?,?,?,?,?,?,?,?,?)",(
                str(record.action_id),str(record.alert_id),record.action.value,record.occurred_at.astimezone(timezone.utc).isoformat(),
                str(record.actor_id),str(record.acting_role),str(record.permission_id),record.responsibility.value,reason,str(record.correlation_id)))
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0291: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self,alert_id:BusinessId):
        rows=self._connection.execute(f"SELECT * FROM {self.TABLE} WHERE alert_id=? ORDER BY occurred_at,action_id",(str(alert_id),)).fetchall()
        return tuple(GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord(
            BusinessId(str(r[0])),BusinessId(str(r[1])),GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction(str(r[2])),
            datetime.fromisoformat(str(r[3])),BusinessId(str(r[4])),BusinessId(str(r[5])),BusinessId(str(r[6])),GlobalSecurityResponsibilityType(str(r[7])),str(r[8]),CorrelationId(str(r[9]))) for r in rows)

class AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryService:
    def __init__(self,responsibilities:SQLiteGlobalSecurityResponsibilityRepository,identities:SQLiteIdentityRepository,alerts:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryRepository,audit:SQLiteGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRepository):
        self._responsibilities=responsibilities
        self._identities=identities
        self._alerts=alerts
        self._audit=audit
    def acknowledge(self,alert_id:BusinessId,*,action_id:BusinessId,acknowledged_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,acknowledged_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_ACKNOWLEDGE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE,unavailable_user_ids)
    def resolve(self,alert_id:BusinessId,*,action_id:BusinessId,resolved_at:datetime,acting_role:BusinessId,reason:str,correlation_id:CorrelationId,unavailable_user_ids:frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,resolved_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ATTEMPT_ACTION_ATTEMPT_ACTION_ATTEMPT_RESOLVE,GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.RESOLVE,unavailable_user_ids)
    def _execute(self,alert_id,action_id,at,acting_role,reason,correlation_id,permission,action,unavailable_user_ids):
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0287: Bearbeitungszeitpunkte benoetigen eine Zeitzone.")
        instant=at.astimezone(timezone.utc)
        authority=self._responsibilities.resolve(at=instant,unavailable_user_ids=unavailable_user_ids)
        authorization=self._identities.create_authorization_service().authorize(self._identities.create_context(authority.user.user_id),permission,at=instant)
        if not authorization.allowed:
            raise PermissionError(f"ERR-KICAD-0292: {authorization.reason}")
        if acting_role not in authorization.matched_roles:
            raise PermissionError("ERR-KICAD-0293: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht.")
        alert=self._alerts.acknowledge(alert_id,acknowledged_at=instant,acknowledged_by=authority.user.user_id,reason=reason) if action is GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction.ACKNOWLEDGE else self._alerts.resolve(alert_id,resolved_at=instant,resolved_by=authority.user.user_id,reason=reason)
        record=GlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryActionAuditRecord(action_id,alert_id,action,instant,authority.user.user_id,acting_role,permission,authority.source,reason.strip(),correlation_id)
        self._audit.append(record)
        return AuthorizedGlobalSecurityStaffingReleaseAlertAttemptHistoryActionAttemptHistoryActionAttemptHistoryAction(authority,authorization,alert,record)
