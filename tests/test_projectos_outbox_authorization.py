from datetime import datetime, timezone

import pytest

from projectos import (
    AuthorizationContext,
    AuthorizationService,
    BusinessId,
    CorrelationId,
    DomainEvent,
    ObjectId,
    OutboxAdministrationService,
    PERM_OUTBOX_DEAD_LETTER_RECOVER,
    Role,
    SQLiteAuditRepository,
    SQLiteDeliveryRepository,
    SQLiteOutboxRepository,
    SQLiteUnitOfWork,
    AuthorizedOutboxAdministrationService,
)

NOW = datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc)
ROLE_ADMIN = BusinessId("ROLE-OUTBOX-ADMIN")
USER_ADMIN = BusinessId("USR-OUTBOX-ADMIN")


def make_event() -> DomainEvent:
    return DomainEvent(
        event_id=ObjectId.new(),
        event_type="protection.mcb.created",
        occurred_at=NOW,
        aggregate_id=ObjectId.new(),
        aggregate_business_id=BusinessId("MCB-OUTBOX-0001"),
        aggregate_revision=1,
        correlation_id=CorrelationId.from_sequence(44),
        payload={"source": "test"},
    )


def make_service(connection, authorization):
    outbox = SQLiteOutboxRepository(connection)
    deliveries = SQLiteDeliveryRepository(connection)
    administration = OutboxAdministrationService(outbox, deliveries)
    audit = SQLiteAuditRepository(connection)
    return (
        AuthorizedOutboxAdministrationService(
            authorization, administration, outbox, deliveries, audit
        ),
        outbox,
        deliveries,
        audit,
    )


def allowed_authorization() -> AuthorizationService:
    return AuthorizationService(
        roles={
            ROLE_ADMIN: Role(
                ROLE_ADMIN,
                frozenset({PERM_OUTBOX_DEAD_LETTER_RECOVER}),
            )
        }
    )


def context() -> AuthorizationContext:
    return AuthorizationContext(USER_ADMIN, frozenset({ROLE_ADMIN}))


def prepare_dead_letter(outbox, deliveries, event) -> None:
    outbox.append(event)
    deliveries.mark_failure(
        event.event_id,
        attempts=5,
        error="RuntimeError: Dienst nicht verfügbar",
        next_attempt_at=None,
        dead_letter=True,
    )


def test_autorisierte_wiederaufnahme_erzeugt_audit_eintrag(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    event = make_event()
    with SQLiteUnitOfWork(database) as uow:
        service, outbox, deliveries, audit = make_service(uow.connection, allowed_authorization())
        prepare_dead_letter(outbox, deliveries, event)
        result = service.recover_dead_letter(
            event.event_id,
            context=context(),
            acting_role=ROLE_ADMIN,
            reason="Zielsystem wurde repariert.",
            resumed_at=NOW,
            audit_id=BusinessId("AUD-OUTBOX-0001"),
            correlation_id=CorrelationId.from_sequence(45),
        )
        assert result.authorization.allowed
        assert result.recovery.state.attempts == 0
        assert result.audit_entry.permission_id == PERM_OUTBOX_DEAD_LETTER_RECOVER
        assert audit.verify_integrity()

    with SQLiteUnitOfWork(database) as uow:
        deliveries = SQLiteDeliveryRepository(uow.connection)
        audit = SQLiteAuditRepository(uow.connection)
        assert deliveries.get(event.event_id).status.value == "RETRY"
        assert len(audit.all()) == 1


def test_fehlende_berechtigung_veraendert_keinen_status(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    event = make_event()
    with pytest.raises(PermissionError, match="ERR-AUTH-0001"):
        with SQLiteUnitOfWork(database) as uow:
            service, outbox, deliveries, audit = make_service(uow.connection, AuthorizationService())
            prepare_dead_letter(outbox, deliveries, event)
            service.recover_dead_letter(
                event.event_id,
                context=context(),
                acting_role=ROLE_ADMIN,
                reason="Nicht zulässig.",
                resumed_at=NOW,
                audit_id=BusinessId("AUD-OUTBOX-0002"),
                correlation_id=CorrelationId.from_sequence(46),
            )

    with SQLiteUnitOfWork(database) as uow:
        assert SQLiteOutboxRepository(uow.connection).all() == ()
        assert SQLiteAuditRepository(uow.connection).all() == ()


def test_audit_fehler_rollt_wiederaufnahme_zurueck(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    event = make_event()
    with pytest.raises(ValueError, match="ERR-AUD-0001"):
        with SQLiteUnitOfWork(database) as uow:
            service, outbox, deliveries, audit = make_service(uow.connection, allowed_authorization())
            prepare_dead_letter(outbox, deliveries, event)
            service.recover_dead_letter(
                event.event_id,
                context=context(),
                acting_role=ROLE_ADMIN,
                reason="Erster Versuch.",
                resumed_at=NOW,
                audit_id=BusinessId("AUD-OUTBOX-DUP"),
                correlation_id=CorrelationId.from_sequence(47),
            )
            deliveries.mark_failure(
                event.event_id,
                attempts=5,
                error="erneut fehlgeschlagen",
                next_attempt_at=None,
                dead_letter=True,
            )
            service.recover_dead_letter(
                event.event_id,
                context=context(),
                acting_role=ROLE_ADMIN,
                reason="Zweiter Versuch.",
                resumed_at=NOW,
                audit_id=BusinessId("AUD-OUTBOX-DUP"),
                correlation_id=CorrelationId.from_sequence(48),
            )

    with SQLiteUnitOfWork(database) as uow:
        assert SQLiteOutboxRepository(uow.connection).all() == ()
        assert SQLiteAuditRepository(uow.connection).all() == ()
