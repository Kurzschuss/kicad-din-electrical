from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    KiCadReleaseAttemptSearchFilter,
    KiCadReleaseAttemptSearchService,
    SQLiteKiCadReleaseAttemptAuditRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
USER = BusinessId("USR-0001")
ROLE = BusinessId("ROLE-KICAD-RELEASE")
PERMISSION = BusinessId("PERM-KICAD-RELEASE-DECIDE")


def append(repo, number: int, *, code: str = "ERR-KICAD-0078", actor=USER, role=ROLE):
    return repo.append(
        attempt_id=BusinessId(f"KATT-{number:04d}"),
        project_id=PROJECT,
        attempted_at=NOW + timedelta(minutes=number),
        actor_id=actor,
        acting_role=role,
        permission_id=PERMISSION,
        denial_code=code,
        denial_reason="Freigabe wurde abgelehnt.",
        correlation_id=CorrelationId.from_sequence(number),
    )


def test_combined_filters_and_ordering(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        append(repo, 1)
        append(repo, 2, code="ERR-KICAD-0079")
        service = KiCadReleaseAttemptSearchService(uow.connection)
        page = service.search(KiCadReleaseAttemptSearchFilter(
            project_id=PROJECT, actor_id=USER, acting_role=ROLE,
            permission_id=PERMISSION, denial_code="err-kicad-0079",
            from_timestamp=NOW, until_timestamp=NOW + timedelta(hours=1),
        ))
        assert page.total_items == 1
        assert page.items[0].attempt_id == BusinessId("KATT-0002")


def test_pagination_is_stable(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        for number in range(1, 4):
            append(repo, number)
        page = KiCadReleaseAttemptSearchService(uow.connection).search(page=2, page_size=2)
        assert page.total_items == 3
        assert page.total_pages == 2
        assert page.has_previous and not page.has_next
        assert [str(item.attempt_id) for item in page.items] == ["KATT-0001"]


def test_diagnostic_counts_codes_actors_and_roles(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        append(repo, 1)
        append(repo, 2)
        append(repo, 3, code="ERR-KICAD-0079", actor=BusinessId("USR-0002"), role=BusinessId("ROLE-OTHER"))
        result = KiCadReleaseAttemptSearchService(uow.connection).diagnostic()
        assert result.total_attempts == 3
        assert result.unique_projects == 1
        assert result.unique_actors == 2
        assert result.top_denial_codes[0] == ("ERR-KICAD-0078", 2)
        assert result.first_attempt_at < result.latest_attempt_at


def test_empty_diagnostic_is_defined(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        result = KiCadReleaseAttemptSearchService(uow.connection).diagnostic()
        assert result.total_attempts == 0
        assert result.first_attempt_at is None
        assert result.top_denial_codes == ()


def test_invalid_time_and_pagination_are_rejected(tmp_path) -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0086"):
        KiCadReleaseAttemptSearchFilter(from_timestamp=datetime(2026, 8, 6, 12, 0))
    with pytest.raises(ValueError, match="ERR-KICAD-0087"):
        KiCadReleaseAttemptSearchFilter(
            from_timestamp=NOW + timedelta(hours=1), until_timestamp=NOW
        )
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        service = KiCadReleaseAttemptSearchService(uow.connection)
        with pytest.raises(ValueError, match="ERR-KICAD-0088"):
            service.search(page=0)
        with pytest.raises(ValueError, match="ERR-KICAD-0089"):
            service.search(page_size=201)
