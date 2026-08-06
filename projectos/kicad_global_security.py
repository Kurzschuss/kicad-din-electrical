"""Globale Sicherheitsverantwortung für projektlose KiCad-Sicherheitsalarme."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3

from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository, UserAccount
from .kicad_security_alert_authorization import (
    KiCadSecurityAlertAction,
    PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE,
    PERM_KICAD_SECURITY_ALERT_RESOLVE,
)
from .kicad_security_alert_history import KiCadSecurityAlertRecord, SQLiteKiCadSecurityAlertRepository


class GlobalSecurityResponsibilityType(StrEnum):
    PRIMARY = "PRIMARY"
    DEPUTY = "DEPUTY"


@dataclass(frozen=True, slots=True)
class GlobalSecurityResponsibility:
    responsibility: GlobalSecurityResponsibilityType
    user_id: BusinessId
    assigned_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if self.assigned_at.tzinfo is None or self.assigned_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0117: Die Zuweisung benötigt eine Zeitzone.")
        normalized = self.reason.strip()
        if not normalized:
            raise ValueError("ERR-KICAD-0118: Die globale Sicherheitsverantwortung benötigt eine Begründung.")
        object.__setattr__(self, "assigned_at", self.assigned_at.astimezone(timezone.utc))
        object.__setattr__(self, "reason", normalized)


@dataclass(frozen=True, slots=True)
class GlobalSecurityAuthorityResolution:
    user: UserAccount
    source: GlobalSecurityResponsibilityType
    resolved_at: datetime


@dataclass(frozen=True, slots=True)
class GlobalKiCadSecurityAlertActionAuditRecord:
    action_id: BusinessId
    alert_id: BusinessId
    action: KiCadSecurityAlertAction
    occurred_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    responsibility: GlobalSecurityResponsibilityType
    reason: str
    correlation_id: CorrelationId


@dataclass(frozen=True, slots=True)
class AuthorizedGlobalKiCadSecurityAlertAction:
    authority: GlobalSecurityAuthorityResolution
    authorization: AuthorizationResult
    alert: KiCadSecurityAlertRecord
    audit_record: GlobalKiCadSecurityAlertActionAuditRecord


class SQLiteGlobalSecurityResponsibilityRepository:
    def __init__(self, connection: sqlite3.Connection, identities: SQLiteIdentityRepository) -> None:
        self._connection = connection
        self._identities = identities
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projectos_global_security_responsibilities (
                responsibility TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                reason TEXT NOT NULL
            )"""
        )
        self._connection.commit()

    def assign(self, value: GlobalSecurityResponsibility) -> GlobalSecurityResponsibility:
        user = self._identities.get_user(value.user_id)
        if user is None:
            raise LookupError("ERR-KICAD-0119: Globale Sicherheitsverantwortung verweist auf einen unbekannten Benutzer.")
        if not user.active:
            raise PermissionError("ERR-KICAD-0120: Globale Sicherheitsverantwortung benötigt einen aktiven Benutzer.")
        self._connection.execute(
            "INSERT INTO projectos_global_security_responsibilities VALUES (?, ?, ?, ?) "
            "ON CONFLICT(responsibility) DO UPDATE SET user_id=excluded.user_id, assigned_at=excluded.assigned_at, reason=excluded.reason",
            (value.responsibility.value, str(value.user_id), value.assigned_at.isoformat(), value.reason),
        )
        self._connection.commit()
        return value

    def get(self, responsibility: GlobalSecurityResponsibilityType) -> GlobalSecurityResponsibility | None:
        row = self._connection.execute(
            "SELECT * FROM projectos_global_security_responsibilities WHERE responsibility = ?",
            (responsibility.value,),
        ).fetchone()
        if row is None:
            return None
        return GlobalSecurityResponsibility(
            responsibility, BusinessId(str(row[1])), datetime.fromisoformat(str(row[2])), str(row[3])
        )

    def resolve(self, *, at: datetime, unavailable_user_ids: frozenset[BusinessId] = frozenset()) -> GlobalSecurityAuthorityResolution:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0121: Der Auflösungszeitpunkt benötigt eine Zeitzone.")
        instant = at.astimezone(timezone.utc)
        for source in (GlobalSecurityResponsibilityType.PRIMARY, GlobalSecurityResponsibilityType.DEPUTY):
            responsibility = self.get(source)
            if responsibility is None or responsibility.user_id in unavailable_user_ids:
                continue
            user = self._identities.get_user(responsibility.user_id)
            if user is not None and user.active:
                return GlobalSecurityAuthorityResolution(user, source, instant)
        raise LookupError("ERR-KICAD-0122: Keine verfügbare globale Sicherheitsverantwortung gefunden.")


class SQLiteGlobalKiCadSecurityAlertActionAuditRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projectos_kicad_global_security_alert_action_audit (
                action_id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, action TEXT NOT NULL,
                occurred_at TEXT NOT NULL, actor_id TEXT NOT NULL, acting_role TEXT NOT NULL,
                permission_id TEXT NOT NULL, responsibility TEXT NOT NULL, reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL
            )"""
        )
        self._connection.commit()

    def append(self, record: GlobalKiCadSecurityAlertActionAuditRecord) -> GlobalKiCadSecurityAlertActionAuditRecord:
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0123: Der globale Auditzeitpunkt benötigt eine Zeitzone.")
        if not record.reason.strip():
            raise ValueError("ERR-KICAD-0124: Das globale Bearbeitungsaudit benötigt eine Begründung.")
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_global_security_alert_action_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(record.action_id), str(record.alert_id), record.action.value, record.occurred_at.isoformat(),
                 str(record.actor_id), str(record.acting_role), str(record.permission_id), record.responsibility.value,
                 record.reason.strip(), str(record.correlation_id)),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0125: Die globale Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return record

    def list_for_alert(self, alert_id: BusinessId) -> tuple[GlobalKiCadSecurityAlertActionAuditRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_global_security_alert_action_audit WHERE alert_id = ? ORDER BY occurred_at, action_id",
            (str(alert_id),),
        ).fetchall()
        return tuple(GlobalKiCadSecurityAlertActionAuditRecord(
            BusinessId(str(r[0])), BusinessId(str(r[1])), KiCadSecurityAlertAction(str(r[2])),
            datetime.fromisoformat(str(r[3])), BusinessId(str(r[4])), BusinessId(str(r[5])),
            BusinessId(str(r[6])), GlobalSecurityResponsibilityType(str(r[7])), str(r[8]), CorrelationId(str(r[9]))
        ) for r in rows)


class AuthorizedGlobalKiCadSecurityAlertService:
    """Bearbeitet ausschließlich projektlose Alarme über globale Sicherheitsverantwortung."""

    def __init__(self, responsibilities: SQLiteGlobalSecurityResponsibilityRepository,
                 identities: SQLiteIdentityRepository, alerts: SQLiteKiCadSecurityAlertRepository,
                 audit: SQLiteGlobalKiCadSecurityAlertActionAuditRepository) -> None:
        self._responsibilities = responsibilities
        self._identities = identities
        self._alerts = alerts
        self._audit = audit

    def acknowledge(self, alert_id: BusinessId, *, action_id: BusinessId, acknowledged_at: datetime,
                    acting_role: BusinessId, reason: str, correlation_id: CorrelationId,
                    unavailable_user_ids: frozenset[BusinessId] = frozenset()) -> AuthorizedGlobalKiCadSecurityAlertAction:
        return self._execute(alert_id, action_id=action_id, at=acknowledged_at, acting_role=acting_role,
                             reason=reason, correlation_id=correlation_id,
                             permission=PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE,
                             action=KiCadSecurityAlertAction.ACKNOWLEDGE,
                             unavailable_user_ids=unavailable_user_ids)

    def resolve(self, alert_id: BusinessId, *, action_id: BusinessId, resolved_at: datetime,
                acting_role: BusinessId, reason: str, correlation_id: CorrelationId,
                unavailable_user_ids: frozenset[BusinessId] = frozenset()) -> AuthorizedGlobalKiCadSecurityAlertAction:
        return self._execute(alert_id, action_id=action_id, at=resolved_at, acting_role=acting_role,
                             reason=reason, correlation_id=correlation_id,
                             permission=PERM_KICAD_SECURITY_ALERT_RESOLVE,
                             action=KiCadSecurityAlertAction.RESOLVE,
                             unavailable_user_ids=unavailable_user_ids)

    def _execute(self, alert_id: BusinessId, *, action_id: BusinessId, at: datetime, acting_role: BusinessId,
                 reason: str, correlation_id: CorrelationId, permission: BusinessId,
                 action: KiCadSecurityAlertAction, unavailable_user_ids: frozenset[BusinessId]) -> AuthorizedGlobalKiCadSecurityAlertAction:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0108: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
        instant = at.astimezone(timezone.utc)
        current = self._alerts.get(alert_id)
        if current.project_id is not None:
            raise ValueError("ERR-KICAD-0126: Ein projektbezogener Alarm darf nicht global autorisiert werden.")
        authority = self._responsibilities.resolve(at=instant, unavailable_user_ids=unavailable_user_ids)
        context = self._identities.create_context(authority.user.user_id)
        authorization = self._identities.create_authorization_service().authorize(context, permission, at=instant)
        if not authorization.allowed:
            raise PermissionError(f"ERR-KICAD-0127: {authorization.reason}")
        if acting_role not in authorization.matched_roles:
            raise PermissionError("ERR-KICAD-0128: Die handelnde Rolle erteilt die globale Alarmbearbeitungsberechtigung nicht.")
        if action is KiCadSecurityAlertAction.ACKNOWLEDGE:
            updated = self._alerts.acknowledge(alert_id, acknowledged_at=instant, acknowledged_by=authority.user.user_id, reason=reason)
        else:
            updated = self._alerts.resolve(alert_id, resolved_at=instant, resolved_by=authority.user.user_id, reason=reason)
        record = GlobalKiCadSecurityAlertActionAuditRecord(
            action_id, alert_id, action, instant, authority.user.user_id, acting_role,
            permission, authority.source, reason.strip(), correlation_id,
        )
        self._audit.append(record)
        return AuthorizedGlobalKiCadSecurityAlertAction(authority, authorization, updated, record)
