"""Autorisierte Dead-Letter-Wiederaufnahme mit persistentem Audit-Nachweis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .audit import AuditEntry
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService
from .identifiers import BusinessId, CorrelationId, ObjectId
from .outbox import SQLiteOutboxRepository
from .outbox_admin import DeadLetterRecovery, OutboxAdministrationService
from .sqlite_audit import SQLiteAuditRepository

PERM_OUTBOX_DEAD_LETTER_RECOVER = BusinessId("PERM-OUTBOX-DEAD-LETTER-RECOVER")


@dataclass(frozen=True, slots=True)
class AuthorizedDeadLetterRecovery:
    """Ergebnis einer autorisierten und auditierten Wiederaufnahme."""

    authorization: AuthorizationResult
    recovery: DeadLetterRecovery
    audit_entry: AuditEntry


class AuthorizedOutboxAdministrationService:
    """Verbindet Autorisierung, Dead-Letter-Wiederaufnahme und Audit-Trail."""

    def __init__(
        self,
        authorization: AuthorizationService,
        administration: OutboxAdministrationService,
        outbox: SQLiteOutboxRepository,
        audit: SQLiteAuditRepository,
    ) -> None:
        self._authorization = authorization
        self._administration = administration
        self._outbox = outbox
        self._audit = audit

    def recover_dead_letter(
        self,
        event_id: ObjectId,
        *,
        context: AuthorizationContext,
        acting_role: BusinessId,
        reason: str,
        resumed_at: datetime,
        audit_id: BusinessId,
        correlation_id: CorrelationId,
    ) -> AuthorizedDeadLetterRecovery:
        """Nimmt ein Dead Letter nach erfolgreicher Berechtigungsprüfung wieder auf.

        Die aufrufende ``SQLiteUnitOfWork`` bildet die Transaktionsgrenze. Schlägt
        der Audit-Eintrag fehl, wird dadurch auch die Wiederaufnahme zurückgerollt.
        """
        if resumed_at.tzinfo is None:
            raise ValueError("resumed_at benötigt einen Zeitzonenbezug.")
        instant = resumed_at.astimezone(timezone.utc)
        decision = self._authorization.authorize(
            context,
            PERM_OUTBOX_DEAD_LETTER_RECOVER,
            at=instant,
        )
        if not decision.allowed:
            raise PermissionError(f"ERR-AUTH-0001: {decision.reason}")
        if acting_role not in context.role_ids:
            raise PermissionError("ERR-AUTH-0002: Die handelnde Rolle ist im Kontext nicht aktiv.")

        message = next(
            (item for item in self._outbox.all() if item.event.event_id == event_id),
            None,
        )
        if message is None:
            raise LookupError("ERR-OUT-0004: Outbox-Nachricht wurde nicht gefunden.")

        previous_state = self._administration._deliveries.get(event_id)  # interne atomare Orchestrierung
        recovery = self._administration.recover_dead_letter(
            event_id,
            actor_id=context.user_id,
            reason=reason,
            resumed_at=instant,
        )
        audit_entry = AuditEntry(
            audit_id=audit_id,
            occurred_at=instant,
            actor_id=context.user_id,
            acting_role=acting_role,
            permission_id=PERM_OUTBOX_DEAD_LETTER_RECOVER,
            object_id=event_id,
            object_business_id=message.event.aggregate_business_id,
            action="outbox_dead_letter_recovered",
            reason=recovery.reason,
            correlation_id=correlation_id,
            previous_values={
                "status": previous_state.status.value,
                "attempts": previous_state.attempts,
                "last_error": previous_state.last_error,
            },
            new_values={
                "status": recovery.state.status.value,
                "attempts": recovery.state.attempts,
                "next_attempt_at": recovery.state.next_attempt_at,
            },
            previous_hash=self._audit.last_hash(),
        )
        self._audit.append(audit_entry)
        return AuthorizedDeadLetterRecovery(decision, recovery, audit_entry)
