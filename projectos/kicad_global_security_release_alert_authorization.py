"""Autorisierung und Audit der Bearbeitung globaler Besetzungsfreigabealarme."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, GlobalSecurityResponsibilityType, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_release_alert_history import GlobalSecurityStaffingReleaseAlertRecord, SQLiteGlobalSecurityStaffingReleaseAlertRepository

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE = BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ACKNOWLEDGE")
PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_RESOLVE = BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-RESOLVE")

class GlobalSecurityStaffingReleaseAlertAction(StrEnum):
    ACKNOWLEDGE="ACKNOWLEDGE"
    RESOLVE="RESOLVE"

@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAlertActionAuditRecord:
    action_id: BusinessId
    alert_id: BusinessId
    action: GlobalSecurityStaffingReleaseAlertAction
    occurred_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    responsibility: GlobalSecurityResponsibilityType
    reason: str
    correlation_id: CorrelationId

@dataclass(frozen=True, slots=True)
class AuthorizedGlobalSecurityStaffingReleaseAlertAction:
    authority: GlobalSecurityAuthorityResolution
    authorization: AuthorizationResult
    alert: GlobalSecurityStaffingReleaseAlertRecord
    audit_record: GlobalSecurityStaffingReleaseAlertActionAuditRecord

class SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection=connection
        connection.execute("""CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_alert_action_audit (
        action_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL, occurred_at TEXT NOT NULL,
        actor_id TEXT NOT NULL, acting_role TEXT NOT NULL, permission_id TEXT NOT NULL, responsibility TEXT NOT NULL,
        reason TEXT NOT NULL, correlation_id TEXT NOT NULL)""")
        connection.commit()
    def append(self, record: GlobalSecurityStaffingReleaseAlertActionAuditRecord):
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None: raise ValueError("ERR-KICAD-0178: Der Auditzeitpunkt benötigt eine Zeitzone.")
        reason=record.reason.strip()
        if not reason: raise ValueError("ERR-KICAD-0179: Das Bearbeitungsaudit benötigt eine Begründung.")
        try:
            self._connection.execute("INSERT INTO projectos_global_security_staffing_release_alert_action_audit VALUES (?,?,?,?,?,?,?,?,?,?)",(str(record.action_id),str(record.alert_id),record.action.value,record.occurred_at.astimezone(timezone.utc).isoformat(),str(record.actor_id),str(record.acting_role),str(record.permission_id),record.responsibility.value,reason,str(record.correlation_id)))
            self._connection.commit()
        except sqlite3.IntegrityError as exc: raise ValueError("ERR-KICAD-0180: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record
    def list_for_alert(self, alert_id: BusinessId):
        rows=self._connection.execute("SELECT * FROM projectos_global_security_staffing_release_alert_action_audit WHERE alert_id=? ORDER BY occurred_at,action_id",(str(alert_id),)).fetchall()
        return tuple(GlobalSecurityStaffingReleaseAlertActionAuditRecord(BusinessId(str(r[0])),BusinessId(str(r[1])),GlobalSecurityStaffingReleaseAlertAction(str(r[2])),datetime.fromisoformat(str(r[3])),BusinessId(str(r[4])),BusinessId(str(r[5])),BusinessId(str(r[6])),GlobalSecurityResponsibilityType(str(r[7])),str(r[8]),CorrelationId(str(r[9]))) for r in rows)

class AuthorizedGlobalSecurityStaffingReleaseAlertService:
    def __init__(self, responsibilities: SQLiteGlobalSecurityResponsibilityRepository, identities: SQLiteIdentityRepository, alerts: SQLiteGlobalSecurityStaffingReleaseAlertRepository, audit: SQLiteGlobalSecurityStaffingReleaseAlertActionAuditRepository):
        self._responsibilities=responsibilities; self._identities=identities; self._alerts=alerts; self._audit=audit
    def acknowledge(self, alert_id: BusinessId, *, action_id: BusinessId, acknowledged_at: datetime, acting_role: BusinessId, reason: str, correlation_id: CorrelationId, unavailable_user_ids: frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,acknowledged_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_ACKNOWLEDGE,GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE,unavailable_user_ids)
    def resolve(self, alert_id: BusinessId, *, action_id: BusinessId, resolved_at: datetime, acting_role: BusinessId, reason: str, correlation_id: CorrelationId, unavailable_user_ids: frozenset[BusinessId]=frozenset()):
        return self._execute(alert_id,action_id,resolved_at,acting_role,reason,correlation_id,PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_ALERT_RESOLVE,GlobalSecurityStaffingReleaseAlertAction.RESOLVE,unavailable_user_ids)
    def _execute(self, alert_id, action_id, at, acting_role, reason, correlation_id, permission, action, unavailable_user_ids):
        if at.tzinfo is None or at.utcoffset() is None: raise ValueError("ERR-KICAD-0176: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
        instant=at.astimezone(timezone.utc)
        authority=self._responsibilities.resolve(at=instant,unavailable_user_ids=unavailable_user_ids)
        authorization=self._identities.create_authorization_service().authorize(self._identities.create_context(authority.user.user_id),permission,at=instant)
        if not authorization.allowed: raise PermissionError(f"ERR-KICAD-0181: {authorization.reason}")
        if acting_role not in authorization.matched_roles: raise PermissionError("ERR-KICAD-0182: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht.")
        if action is GlobalSecurityStaffingReleaseAlertAction.ACKNOWLEDGE:
            alert=self._alerts.acknowledge(alert_id,acknowledged_at=instant,acknowledged_by=authority.user.user_id,reason=reason)
        else:
            alert=self._alerts.resolve(alert_id,resolved_at=instant,resolved_by=authority.user.user_id,reason=reason)
        record=GlobalSecurityStaffingReleaseAlertActionAuditRecord(action_id,alert_id,action,instant,authority.user.user_id,acting_role,permission,authority.source,reason.strip(),correlation_id)
        self._audit.append(record)
        return AuthorizedGlobalSecurityStaffingReleaseAlertAction(authority,authorization,alert,record)
