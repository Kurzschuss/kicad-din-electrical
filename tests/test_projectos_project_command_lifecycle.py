from datetime import datetime, timezone

from projectos import (
    BusinessId,
    CommandAdministrationService,
    CommandExecutionRecord,
    CommandExecutionStatus,
    CommandLifecycleService,
    CommandLifecycleState,
    CommandRetryRecord,
    CorrelationId,
    ObjectId,
    SQLiteCommandExecutionRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc)
COMMAND_ID = BusinessId("CMD-LIFECYCLE-0001")
PROJECT_ID = BusinessId("PRJ-0001")
OBJECT_ID = ObjectId.new()


class RetryView:
    def __init__(self, attempts: tuple[CommandRetryRecord, ...] = ()) -> None:
        self._attempts = attempts

    def attempts(self, command_id: BusinessId | None = None) -> tuple[CommandRetryRecord, ...]:
        if command_id is None:
            return self._attempts
        return tuple(item for item in self._attempts if item.command_id == command_id)


def record(status: CommandExecutionStatus) -> CommandExecutionRecord:
    return CommandExecutionRecord(
        command_id=COMMAND_ID,
        command_type="project.setting.change",
        project_id=PROJECT_ID,
        project_object_id=OBJECT_ID,
        payload_hash="a" * 64,
        status=status,
        processed_at=NOW,
        correlation_id=str(CorrelationId.from_sequence(55)),
        message_codes=("ERR-PRJ-CMD-0003",) if status is CommandExecutionStatus.REJECTED else (),
    )


def test_abgelehnte_ausfuehrung_wird_vor_wiederaufnahme_archiviert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record(CommandExecutionStatus.REJECTED))
        administration = CommandAdministrationService(uow.connection, history)
        administration.recover_rejected(
            COMMAND_ID,
            recovery_id=BusinessId("RCV-0001"),
            actor_id=BusinessId("USR-ADMIN"),
            reason="Berechtigung korrigiert",
            recovered_at=NOW,
        )
        view = CommandLifecycleService(administration, RetryView()).get(COMMAND_ID)

        assert view.state is CommandLifecycleState.READY_FOR_RETRY
        assert view.current_execution is None
        assert view.original_execution is not None
        assert view.original_execution.status is CommandExecutionStatus.REJECTED
        assert view.original_execution.message_codes == ("ERR-PRJ-CMD-0003",)
        assert len(view.recoveries) == 1


def test_erfolgreicher_command_wird_ohne_wiederaufnahme_angezeigt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record(CommandExecutionStatus.SUCCEEDED))
        administration = CommandAdministrationService(uow.connection, history)
        view = CommandLifecycleService(administration, RetryView()).get(COMMAND_ID)

        assert view.state is CommandLifecycleState.SUCCEEDED
        assert view.original_execution == view.current_execution
        assert view.recoveries == ()
        assert view.retry_attempts == ()


def test_abgelehnter_folgeversuch_wird_im_lebenszyklus_sichtbar(tmp_path) -> None:
    attempt = CommandRetryRecord(
        attempt_id=BusinessId("ATT-0001"),
        command_id=COMMAND_ID,
        recovery_id=BusinessId("RCV-0001"),
        status=CommandExecutionStatus.REJECTED,
        processed_at=NOW,
        correlation_id=str(CorrelationId.from_sequence(56)),
    )
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        history.append(record(CommandExecutionStatus.REJECTED))
        administration = CommandAdministrationService(uow.connection, history)
        view = CommandLifecycleService(administration, RetryView((attempt,))).get(COMMAND_ID)

        assert view.state is CommandLifecycleState.RETRY_REJECTED
        assert view.retry_attempts == (attempt,)


def test_unbekannter_command_liefert_not_found(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        administration = CommandAdministrationService(uow.connection, history)
        view = CommandLifecycleService(administration, RetryView()).get(COMMAND_ID)
        assert view.state is CommandLifecycleState.NOT_FOUND
        assert view.original_execution is None
