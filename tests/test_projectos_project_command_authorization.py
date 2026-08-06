from datetime import datetime, timezone

import pytest

from projectos import (
    AuthorizationContext,
    AuthorizationService,
    AuthorizedCommandAdministrationService,
    BusinessId,
    CommandAdministrationService,
    CommandExecutionRecord,
    CommandExecutionStatus,
    CorrelationId,
    ObjectId,
    PERM_PROJECT_COMMAND_RECOVER,
    Role,
    SQLiteAuditRepository,
    SQLiteCommandExecutionRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 9, 15, tzinfo=timezone.utc)
USER = BusinessId("USR-ADMIN")
ROLE = BusinessId("ROLE-COMMAND-ADMIN")
COMMAND = BusinessId("CMD-REJECTED-0001")
PROJECT = BusinessId("PRJ-0001")
OBJECT = ObjectId.new()


def configure(uow: SQLiteUnitOfWork, *, allowed: bool = True):
    history = SQLiteCommandExecutionRepository(uow.connection)
    history.append(
        CommandExecutionRecord(
            command_id=COMMAND,
            command_type="project.setting.change",
            project_id=PROJECT,
            project_object_id=OBJECT,
            payload_hash="a" * 64,
            status=CommandExecutionStatus.REJECTED,
            processed_at=NOW,
            correlation_id=str(CorrelationId.from_sequence(53)),
            message_codes=("ERR-PRJ-CMD-0003",),
        )
    )
    administration = CommandAdministrationService(uow.connection, history)
    permissions = frozenset({PERM_PROJECT_COMMAND_RECOVER}) if allowed else frozenset()
    authorization = AuthorizationService(roles={ROLE: Role(ROLE, permissions)})
    context = AuthorizationContext(USER, frozenset({ROLE}), project_id=PROJECT)
    service = AuthorizedCommandAdministrationService(
        authorization,
        administration,
        SQLiteAuditRepository(uow.connection),
    )
    return service, administration, context


def test_autorisierte_wiederaufnahme_wird_auditiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        service, administration, context = configure(uow)
        result = service.recover_rejected(
            COMMAND,
            recovery_id=BusinessId("RCV-CMD-0001"),
            context=context,
            acting_role=ROLE,
            reason="Berechtigung wurde korrigiert.",
            recovered_at=NOW,
            audit_id=BusinessId("AUD-CMD-0001"),
            correlation_id=CorrelationId.from_sequence(54),
        )
        assert result.authorization.allowed is True
        assert administration.get(COMMAND) is None
        assert result.audit_entry.permission_id == PERM_PROJECT_COMMAND_RECOVER
        assert result.audit_entry.new_values["status"] == "READY_FOR_RETRY"

    with SQLiteUnitOfWork(database) as uow:
        audit = SQLiteAuditRepository(uow.connection)
        assert len(audit.all()) == 1
        assert audit.verify_integrity() is True


def test_fehlende_berechtigung_verhindert_wiederaufnahme_und_audit(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with pytest.raises(PermissionError, match="ERR-AUTH-0001"):
        with SQLiteUnitOfWork(database) as uow:
            service, _, context = configure(uow, allowed=False)
            service.recover_rejected(
                COMMAND,
                recovery_id=BusinessId("RCV-CMD-0002"),
                context=context,
                acting_role=ROLE,
                reason="Nicht erlaubt.",
                recovered_at=NOW,
                audit_id=BusinessId("AUD-CMD-0002"),
                correlation_id=CorrelationId.from_sequence(55),
            )

    with SQLiteUnitOfWork(database) as uow:
        assert SQLiteCommandExecutionRepository(uow.connection).get(COMMAND) is None
        assert SQLiteAuditRepository(uow.connection).all() == ()


def test_inaktive_handelnde_rolle_wird_abgelehnt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _, context = configure(uow)
        with pytest.raises(PermissionError, match="ERR-AUTH-0002"):
            service.recover_rejected(
                COMMAND,
                recovery_id=BusinessId("RCV-CMD-0003"),
                context=context,
                acting_role=BusinessId("ROLE-OTHER"),
                reason="Falsche Rolle.",
                recovered_at=NOW,
                audit_id=BusinessId("AUD-CMD-0003"),
                correlation_id=CorrelationId.from_sequence(56),
            )
