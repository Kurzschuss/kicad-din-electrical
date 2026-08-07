from datetime import datetime, timezone

from projectos import (
    BusinessId,
    Command,
    CorrelationId,
    IdempotentProjectCommandPipeline,
    ObjectId,
    Result,
    SQLiteCommandExecutionRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
OBJECT_ID = ObjectId.new()


class StubPipeline:
    def __init__(self) -> None:
        self.calls = 0

    def dispatch(self, command, **kwargs):
        self.calls += 1
        return Result.success({"processed": str(command.command_id)}, correlation_id=command.correlation_id)


def create_command(command_id: str, payload: dict[str, object] | None = None) -> Command:
    return Command(
        command_id=BusinessId(command_id),
        command_type="project.setting.change",
        correlation_id=CorrelationId.from_sequence(51),
        issued_at=NOW,
        payload=payload or {"value": 1},
    )


def dispatch(service, command):
    return service.dispatch(
        command,
        project_id=PROJECT,
        project_object_id=OBJECT_ID,
        audit_id=BusinessId("AUD-CMD-0051"),
        reason="Idempotenztest",
    )


def test_identische_wiederholung_wird_nicht_erneut_ausgefuehrt(tmp_path) -> None:
    stub = StubPipeline()
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = IdempotentProjectCommandPipeline(
            stub, SQLiteCommandExecutionRepository(uow.connection)
        )
        first = dispatch(service, create_command("CMD-0051-0001"))
        second = dispatch(service, create_command("CMD-0051-0001"))

        assert first.is_success is True
        assert first.value.replayed is False
        assert second.is_success is True
        assert second.value.replayed is True
        assert stub.calls == 1


def test_abweichender_inhalt_mit_gleicher_command_id_wird_abgewiesen(tmp_path) -> None:
    stub = StubPipeline()
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = IdempotentProjectCommandPipeline(
            stub, SQLiteCommandExecutionRepository(uow.connection)
        )
        assert dispatch(service, create_command("CMD-0051-0002", {"value": 1})).is_success
        conflict = dispatch(service, create_command("CMD-0051-0002", {"value": 2}))

        assert conflict.is_success is False
        assert str(conflict.errors[0].code) == "ERR-PRJ-CMD-0004"
        assert stub.calls == 1


def test_historie_bleibt_nach_neuem_oeffnen_erhalten(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    command = create_command("CMD-0051-0003")
    with SQLiteUnitOfWork(database) as uow:
        service = IdempotentProjectCommandPipeline(
            StubPipeline(), SQLiteCommandExecutionRepository(uow.connection)
        )
        assert dispatch(service, command).is_success

    replay_stub = StubPipeline()
    with SQLiteUnitOfWork(database) as uow:
        history = SQLiteCommandExecutionRepository(uow.connection)
        service = IdempotentProjectCommandPipeline(replay_stub, history)
        result = dispatch(service, command)
        assert result.is_success is True
        assert result.value.replayed is True
        assert replay_stub.calls == 0
        assert len(history.all()) == 1
