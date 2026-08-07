from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    CommandAdministrationService,
    CommandExecutionRecord,
    CommandExecutionStatus,
    CommandLifecycleService,
    CommandLifecycleState,
    CommandSearchFilter,
    CommandSearchService,
    ObjectId,
    RecoveredCommandExecutionService,
    SQLiteCommandExecutionRepository,
    SQLiteUnitOfWork,
)

PROJECT_A = BusinessId("PRJ-A")
PROJECT_B = BusinessId("PRJ-B")


def record(sequence: int, *, project: BusinessId, status: CommandExecutionStatus, hour: int) -> CommandExecutionRecord:
    return CommandExecutionRecord(
        command_id=BusinessId(f"CMD-{sequence:04d}"),
        command_type="project.setting.change" if sequence != 3 else "project.member.assign",
        project_id=project,
        project_object_id=ObjectId.parse(f"00000000-0000-0000-0000-{sequence:012d}"),
        payload_hash=f"hash-{sequence}",
        status=status,
        processed_at=datetime(2026, 8, 6, hour, 0, tzinfo=timezone.utc),
        correlation_id=f"COR-{sequence:04d}",
        message_codes=() if status is CommandExecutionStatus.SUCCEEDED else ("ERR-TEST",),
    )


def service(uow: SQLiteUnitOfWork) -> tuple[CommandSearchService, SQLiteCommandExecutionRepository]:
    history = SQLiteCommandExecutionRepository(uow.connection)
    administration = CommandAdministrationService(uow.connection, history)
    retries = RecoveredCommandExecutionService(uow.connection, administration, None)  # type: ignore[arg-type]
    lifecycle = CommandLifecycleService(administration, retries)
    return CommandSearchService(uow.connection, lifecycle), history


def test_suche_liefert_stabil_sortierte_seiten(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        search, history = service(uow)
        history.append(record(1, project=PROJECT_A, status=CommandExecutionStatus.SUCCEEDED, hour=8))
        history.append(record(2, project=PROJECT_A, status=CommandExecutionStatus.REJECTED, hour=9))
        history.append(record(3, project=PROJECT_B, status=CommandExecutionStatus.SUCCEEDED, hour=10))

        first = search.search(page=1, page_size=2)
        second = search.search(page=2, page_size=2)

        assert [str(item.command_id) for item in first.items] == ["CMD-0003", "CMD-0002"]
        assert [str(item.command_id) for item in second.items] == ["CMD-0001"]
        assert first.total_items == 3
        assert first.total_pages == 2
        assert first.has_next is True
        assert second.has_previous is True


def test_filter_koennen_kombiniert_werden(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        search, history = service(uow)
        history.append(record(1, project=PROJECT_A, status=CommandExecutionStatus.SUCCEEDED, hour=8))
        history.append(record(2, project=PROJECT_A, status=CommandExecutionStatus.REJECTED, hour=9))
        history.append(record(3, project=PROJECT_B, status=CommandExecutionStatus.SUCCEEDED, hour=10))

        result = search.search(
            CommandSearchFilter(
                project_id=PROJECT_A,
                state=CommandLifecycleState.REJECTED,
                command_type="PROJECT.SETTING.CHANGE",
                text="cor-0002",
            )
        )

        assert len(result.items) == 1
        assert result.items[0].command_id == BusinessId("CMD-0002")


def test_zeitfilter_ist_einschliesslich(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        search, history = service(uow)
        history.append(record(1, project=PROJECT_A, status=CommandExecutionStatus.SUCCEEDED, hour=8))
        history.append(record(2, project=PROJECT_A, status=CommandExecutionStatus.REJECTED, hour=9))

        result = search.search(
            CommandSearchFilter(
                processed_from=datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc),
                processed_until=datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc),
            )
        )

        assert [item.command_id for item in result.items] == [BusinessId("CMD-0002")]


def test_ungueltige_pagination_und_zeitfilter_werden_abgelehnt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        search, _ = service(uow)
        with pytest.raises(ValueError, match="Seitennummer"):
            search.search(page=0)
        with pytest.raises(ValueError, match="Seitengröße"):
            search.search(page_size=201)

    with pytest.raises(ValueError, match="Zeitzonenbezug"):
        CommandSearchFilter(processed_from=datetime(2026, 8, 6, 9, 0))
    with pytest.raises(ValueError, match="processed_from"):
        CommandSearchFilter(
            processed_from=datetime(2026, 8, 6, 10, 0, tzinfo=timezone.utc),
            processed_until=datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc),
        )
