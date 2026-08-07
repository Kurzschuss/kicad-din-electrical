from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    CommandAdministrationService,
    CommandExecutionRecord,
    CommandExecutionStatus,
    CorrelationId,
    ObjectId,
    SQLiteCommandExecutionRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 9, 30, tzinfo=timezone.utc)


def record(command_id: str, status: CommandExecutionStatus) -> CommandExecutionRecord:
    return CommandExecutionRecord(
        command_id=BusinessId(command_id),
        command_type="project.setting.change",
        project_id=BusinessId("PRJ-0001"),
        project_object_id=ObjectId.new(),
        payload_hash="a" * 64,
        status=status,
        processed_at=NOW,
        correlation_id=str(CorrelationId.from_sequence(52)),
    )


def test_diagnose_und_statusfilter(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record("CMD-0001", CommandExecutionStatus.SUCCEEDED))
        history.append(record("CMD-0002", CommandExecutionStatus.REJECTED))
        service = CommandAdministrationService(uow.connection, history)
        diagnostic = service.diagnostic()
        assert (diagnostic.total, diagnostic.succeeded, diagnostic.rejected) == (2, 1, 1)
        assert [item.command_id for item in service.list_by_status(CommandExecutionStatus.REJECTED)] == [BusinessId("CMD-0002")]


def test_abgelehnter_command_kann_wieder_freigegeben_werden(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record("CMD-0003", CommandExecutionStatus.REJECTED))
        service = CommandAdministrationService(uow.connection, history)
        recovery = service.recover_rejected(
            BusinessId("CMD-0003"),
            recovery_id=BusinessId("REC-0001"),
            actor_id=BusinessId("USR-ADMIN"),
            reason="Berechtigung wurde korrigiert.",
            recovered_at=NOW,
        )
        assert recovery.command_id == BusinessId("CMD-0003")
        assert history.get(BusinessId("CMD-0003")) is None

    with SQLiteUnitOfWork(database) as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        service = CommandAdministrationService(uow.connection, history)
        assert len(service.recoveries()) == 1


def test_erfolgreicher_command_darf_nicht_wiederaufgenommen_werden(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record("CMD-0004", CommandExecutionStatus.SUCCEEDED))
        service = CommandAdministrationService(uow.connection, history)
        with pytest.raises(ValueError, match="ERR-PRJ-CMD-0007"):
            service.recover_rejected(
                BusinessId("CMD-0004"),
                recovery_id=BusinessId("REC-0002"),
                actor_id=BusinessId("USR-ADMIN"),
                reason="Nicht zulässig.",
                recovered_at=NOW,
            )
