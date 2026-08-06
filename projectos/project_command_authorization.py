"""Autorisierte und auditierte Wiederaufnahme abgelehnter ProjectOS-Commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .audit import AuditEntry
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService
from .identifiers import BusinessId, CorrelationId
from .project_command_admin import CommandAdministrationService, CommandRecoveryRecord
from .sqlite_audit import SQLiteAuditRepository

PERM_PROJECT_COMMAND_RECOVER = BusinessId("PERM-PROJECT-COMMAND-RECOVER")


@dataclass(frozen=True, slots=True)
class AuthorizedCommandRecovery:
    """Ergebnis einer autorisierten und auditierten Command-Wiederaufnahme."""

    authorization: AuthorizationResult
    recovery: CommandRecoveryRecord
    audit_entry: AuditEntry


class AuthorizedCommandAdministrationService:
    """Verbindet Autorisierung, Command-Wiederaufnahme und Audit-Trail."""

    def __init__(
        self,
        authorization: AuthorizationService,
        administration: CommandAdministrationService,
        audit: SQLiteAuditRepository,
    ) -> None:
        self._authorization = authorization
        self._administration = administration
        self._audit = audit

    def recover_rejected(
        self,
        command_id: BusinessId,
        *,
        recovery_id: BusinessId,
        context: AuthorizationContext,
        acting_role: BusinessId,
        reason: str,
        recovered_at: datetime,
        audit_id: BusinessId,
        correlation_id: CorrelationId,
    ) -> AuthorizedCommandRecovery:
        """Gibt einen abgelehnten Command nach erfolgreicher Prüfung erneut frei.

        Die aufrufende ``SQLiteUnitOfWork`` bildet die Transaktionsgrenze. Schlägt
        das Audit fehl, werden Wiederaufnahme und Historienänderung zurückgerollt.
        """
        if recovered_at.tzinfo is None:
            raise ValueError("recovered_at benötigt einen Zeitzonenbezug.")
        instant = recovered_at.astimezone(timezone.utc)
        decision = self._authorization.authorize(
            context,
            PERM_PROJECT_COMMAND_RECOVER,
            at=instant,
        )
        if not decision.allowed:
            raise PermissionError(f"ERR-AUTH-0001: {decision.reason}")
        if acting_role not in context.role_ids:
            raise PermissionError("ERR-AUTH-0002: Die handelnde Rolle ist im Kontext nicht aktiv.")

        previous = self._administration._history.get(command_id)
        if previous is None:
            raise LookupError("ERR-PRJ-CMD-0006: Command wurde nicht gefunden.")

        recovery = self._administration.recover_rejected(
            command_id,
            recovery_id=recovery_id,
            actor_id=context.user_id,
            reason=reason,
            recovered_at=instant,
        )
        audit_entry = AuditEntry(
            audit_id=audit_id,
            occurred_at=instant,
            actor_id=context.user_id,
            acting_role=acting_role,
            permission_id=PERM_PROJECT_COMMAND_RECOVER,
            object_id=previous.project_object_id,
            object_business_id=previous.project_id,
            action="project_command_recovered",
            reason=recovery.reason,
            correlation_id=correlation_id,
            previous_values={
                "command_id": str(previous.command_id),
                "command_type": previous.command_type,
                "status": previous.status.value,
                "payload_hash": previous.payload_hash,
                "message_codes": previous.message_codes,
            },
            new_values={
                "status": "READY_FOR_RETRY",
                "recovery_id": str(recovery.recovery_id),
                "recovered_at": recovery.recovered_at,
            },
            previous_hash=self._audit.last_hash(),
        )
        self._audit.append(audit_entry)
        return AuthorizedCommandRecovery(decision, recovery, audit_entry)
