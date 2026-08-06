from datetime import datetime, timezone

from projectos import (
    BusinessId,
    Command,
    CommandExecutionRecord,
    CommandExecutionStatus,
    CommandRecoveryRecord,
    CorrelationId,
    IdempotentProjectCommandResult,
    ObjectId,
    RecoveredCommandExecutionService,
    Result,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc)
COMMAND_ID = BusinessId("CMD-RETRY-0001")
RECOVERY_ID = BusinessId("RCV-0001")
PROJECT_ID = BusinessId("PRJ-0001")
OBJECT_ID = ObjectId.new()


class FakeAdministration:
    def __init__(self, recovery: CommandRecoveryRecord | None) -> None:
        self.recovery = recovery

    def get_recovery(self, recovery_id: BusinessId) -> CommandRecoveryRecord | None:
        return self.recovery if self.recovery and self.recovery.recovery_id == recovery_id else None


class FakePipeline:
    def __init__(self) -> None:
        self.calls = 0

    def dispatch(self, command: Command, **kwargs):
        self.calls += 1
        record = CommandExecutionRecord(
            command_id=command.command_id,
            command_type=command.command_type,
            project_id=kwargs["project_id"],
            project_object_id=kwargs["project_object_id"],
            payload_hash="a" * 64,
            status=CommandExecutionStatus.SUCCEEDED,
            processed_at=NOW,
            correlation_id=str(command.correlation_id),
        )
        return Result.success(
            IdempotentProjectCommandResult(record, replayed=False),
            correlation_id=command.correlation_id,
        )


def command(command_id: BusinessId = COMMAND_ID) -> Command:
    return Command(
        command_id=command_id,
        command_type="project.setting.change",
        correlation_id=CorrelationId.from_sequence(54),
        issued_at=NOW,
        payload={"value": 1},
    )


def recovery(command_id: BusinessId = COMMAND_ID) -> CommandRecoveryRecord:
    return CommandRecoveryRecord(
        RECOVERY_ID,
        command_id,
        BusinessId("USR-ADMIN"),
        "Ursache behoben",
        NOW,
    )


def execute(service: RecoveredCommandExecutionService, cmd: Command):
    return service.execute(
        cmd,
        recovery_id=RECOVERY_ID,
        attempt_id=BusinessId("TRY-0001"),
        project_id=PROJECT_ID,
        project_object_id=OBJECT_ID,
        audit_id=BusinessId("AUD-RETRY-0001"),
        reason="Erneuter Versuch nach Freigabe",
    )


def test_folgeversuch_wird_verknuepft_und_persistiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = FakePipeline()
        service = RecoveredCommandExecutionService(
            uow.connection, FakeAdministration(recovery()), pipeline
        )
        result = execute(service, command())
        assert result.is_success
        assert result.value.retry.status is CommandExecutionStatus.SUCCEEDED
        assert result.value.retry.recovery_id == RECOVERY_ID
        assert pipeline.calls == 1
        assert service.attempts(COMMAND_ID) == (result.value.retry,)


def test_falsche_wiederaufnahme_wird_abgelehnt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = FakePipeline()
        service = RecoveredCommandExecutionService(uow.connection, FakeAdministration(None), pipeline)
        result = execute(service, command())
        assert not result.is_success
        assert str(result.errors[0].code) == "ERR-PRJ-CMD-0009"
        assert pipeline.calls == 0


def test_wiederaufnahme_muss_zum_command_gehoeren(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = FakePipeline()
        service = RecoveredCommandExecutionService(
            uow.connection,
            FakeAdministration(recovery(BusinessId("CMD-OTHER-0001"))),
            pipeline,
        )
        result = execute(service, command())
        assert not result.is_success
        assert str(result.errors[0].code) == "ERR-PRJ-CMD-0010"
        assert pipeline.calls == 0


def test_wiederaufnahme_darf_nur_einen_folgeversuch_erzeugen(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = FakePipeline()
        service = RecoveredCommandExecutionService(
            uow.connection, FakeAdministration(recovery()), pipeline
        )
        assert execute(service, command()).is_success
        second = execute(service, command())
        assert not second.is_success
        assert str(second.errors[0].code) == "ERR-PRJ-CMD-0011"
        assert pipeline.calls == 1
