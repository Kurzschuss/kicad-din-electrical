"""Autorisierung und unveränderliches Audit der KiCad-Sicherheitsalarmbearbeitung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_security_alert_history import (
    KiCadSecurityAlertRecord,
    SQLiteKiCadSecurityAlertRepository,
)
from .project_authorization import (
    ProjectActionAuthorizationResult,
    ProjectActionAuthorizationService,
)


PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE = BusinessId("PERM-KICAD-SECURITY-ALERT-ACKNOWLEDGE")
PERM_KICAD_SECURITY_ALERT_RESOLVE = BusinessId("PERM-KICAD-SECURITY-ALERT-RESOLVE")


class KiCadSecurityAlertAction(StrEnum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    RESOLVE = "RESOLVE"


@dataclass(frozen=True, slots=True)
class KiCadSecurityAlertActionAuditRecord:
    action_id: BusinessId
    alert_id: BusinessId
    project_id: BusinessId
    action: KiCadSecurityAlertAction
    occurred_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    reason: str
    correlation_id: CorrelationId


@dataclass(frozen=True, slots=True)
class AuthorizedKiCadSecurityAlertAction:
    authorization: ProjectActionAuthorizationResult
    alert: KiCadSecurityAlertRecord
    audit_record: KiCadSecurityAlertActionAuditRecord


class SQLiteKiCadSecurityAlertActionAuditRepository:
    """Nur anhängbares Audit autorisierter Alarmstatusänderungen."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_kicad_security_alert_action_audit (
                action_id TEXT PRIMARY KEY,
                alert_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                action TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                acting_role TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_kicad_alert_action_alert_time "
            "ON projectos_kicad_security_alert_action_audit(alert_id, occurred_at ASC, action_id ASC)"
        )
        self._connection.commit()

    def append(
        self,
        *,
        action_id: BusinessId,
        alert_id: BusinessId,
        project_id: BusinessId,
        action: KiCadSecurityAlertAction,
        occurred_at: datetime,
        actor_id: BusinessId,
        acting_role: BusinessId,
        permission_id: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
    ) -> KiCadSecurityAlertActionAuditRecord:
        normalized = reason.strip()
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0110: Der Auditzeitpunkt benötigt eine Zeitzone.")
        if not normalized:
            raise ValueError("ERR-KICAD-0111: Die Alarmbearbeitung benötigt eine Auditbegründung.")
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_security_alert_action_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(action_id), str(alert_id), str(project_id), action.value,
                    occurred_at.isoformat(), str(actor_id), str(acting_role),
                    str(permission_id), normalized, str(correlation_id),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0112: Die Alarmbearbeitungskennung ist bereits vorhanden.") from exc
        return self.get(action_id)

    def get(self, action_id: BusinessId) -> KiCadSecurityAlertActionAuditRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_kicad_security_alert_action_audit WHERE action_id = ?",
            (str(action_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0113: Alarmbearbeitungs-Auditeintrag wurde nicht gefunden.")
        return _decode_action(row)

    def list_for_alert(self, alert_id: BusinessId) -> tuple[KiCadSecurityAlertActionAuditRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_security_alert_action_audit WHERE alert_id = ? "
            "ORDER BY occurred_at ASC, action_id ASC",
            (str(alert_id),),
        ).fetchall()
        return tuple(_decode_action(row) for row in rows)


class AuthorizedKiCadSecurityAlertService:
    """Verbindet Projektvollmacht, Rollenberechtigung, Statusänderung und Audit."""

    def __init__(
        self,
        authorization: ProjectActionAuthorizationService,
        alerts: SQLiteKiCadSecurityAlertRepository,
        audit: SQLiteKiCadSecurityAlertActionAuditRepository,
    ) -> None:
        self._authorization = authorization
        self._alerts = alerts
        self._audit = audit

    def acknowledge(
        self,
        alert_id: BusinessId,
        *,
        action_id: BusinessId,
        acknowledged_at: datetime,
        acting_role: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> AuthorizedKiCadSecurityAlertAction:
        return self._execute(
            alert_id=alert_id,
            action_id=action_id,
            at=acknowledged_at,
            acting_role=acting_role,
            reason=reason,
            correlation_id=correlation_id,
            permission=PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE,
            action=KiCadSecurityAlertAction.ACKNOWLEDGE,
            unavailable_user_ids=unavailable_user_ids,
        )

    def resolve(
        self,
        alert_id: BusinessId,
        *,
        action_id: BusinessId,
        resolved_at: datetime,
        acting_role: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> AuthorizedKiCadSecurityAlertAction:
        return self._execute(
            alert_id=alert_id,
            action_id=action_id,
            at=resolved_at,
            acting_role=acting_role,
            reason=reason,
            correlation_id=correlation_id,
            permission=PERM_KICAD_SECURITY_ALERT_RESOLVE,
            action=KiCadSecurityAlertAction.RESOLVE,
            unavailable_user_ids=unavailable_user_ids,
        )

    def _execute(
        self,
        *,
        alert_id: BusinessId,
        action_id: BusinessId,
        at: datetime,
        acting_role: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
        permission: BusinessId,
        action: KiCadSecurityAlertAction,
        unavailable_user_ids: frozenset[BusinessId],
    ) -> AuthorizedKiCadSecurityAlertAction:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0108: Bearbeitungszeitpunkte benötigen eine Zeitzone.")
        instant = at.astimezone(timezone.utc)
        current = self._alerts.get(alert_id)
        if current.project_id is None:
            raise ValueError("ERR-KICAD-0114: Ein projektloser Alarm kann nicht projektbezogen autorisiert werden.")
        authorization = self._authorization.authorize(
            current.project_id,
            permission,
            at=instant,
            unavailable_user_ids=unavailable_user_ids,
        )
        if not authorization.allowed:
            raise PermissionError(f"ERR-KICAD-0115: {authorization.reason}")
        user_authorization = authorization.authorization
        if user_authorization is None or acting_role not in user_authorization.matched_roles:
            raise PermissionError(
                "ERR-KICAD-0116: Die handelnde Rolle erteilt die erforderliche Alarmbearbeitungsberechtigung nicht."
            )
        actor_id = authorization.authority.authorized_user.user_id
        if action is KiCadSecurityAlertAction.ACKNOWLEDGE:
            updated = self._alerts.acknowledge(
                alert_id, acknowledged_at=instant, acknowledged_by=actor_id, reason=reason
            )
        else:
            updated = self._alerts.resolve(
                alert_id, resolved_at=instant, resolved_by=actor_id, reason=reason
            )
        audit_record = self._audit.append(
            action_id=action_id,
            alert_id=alert_id,
            project_id=current.project_id,
            action=action,
            occurred_at=instant,
            actor_id=actor_id,
            acting_role=acting_role,
            permission_id=permission,
            reason=reason,
            correlation_id=correlation_id,
        )
        return AuthorizedKiCadSecurityAlertAction(authorization, updated, audit_record)


def _decode_action(row: tuple[object, ...]) -> KiCadSecurityAlertActionAuditRecord:
    return KiCadSecurityAlertActionAuditRecord(
        action_id=BusinessId(str(row[0])),
        alert_id=BusinessId(str(row[1])),
        project_id=BusinessId(str(row[2])),
        action=KiCadSecurityAlertAction(str(row[3])),
        occurred_at=datetime.fromisoformat(str(row[4])),
        actor_id=BusinessId(str(row[5])),
        acting_role=BusinessId(str(row[6])),
        permission_id=BusinessId(str(row[7])),
        reason=str(row[8]),
        correlation_id=CorrelationId(str(row[9])),
    )
