from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    GlobalSecurityStaffingReleaseAttemptRecord,
    GlobalSecurityStaffingReleaseAttemptSearchFilter,
    GlobalSecurityStaffingReleaseAttemptSearchService,
    SQLiteGlobalSecurityStaffingReleaseAttemptRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 16, 0, tzinfo=timezone.utc)
ROLE_A = BusinessId("ROLE-SECURITY-A")
ROLE_B = BusinessId("ROLE-SECURITY-B")
PERMISSION = BusinessId("PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-DECIDE")
ACTOR = BusinessId("USR-SECURITY")


def seed(uow):
    repo = SQLiteGlobalSecurityStaffingReleaseAttemptRepository(uow.connection)
    repo.append(GlobalSecurityStaffingReleaseAttemptRecord(
        BusinessId("GSEC-ATT-2001"), NOW - timedelta(minutes=20), ACTOR, ROLE_A, PERMISSION,
        "ERR-KICAD-0147", "Falsche Rolle verwendet.", CorrelationId("COR-00002001"),
    ))
    repo.append(GlobalSecurityStaffingReleaseAttemptRecord(
        BusinessId("GSEC-ATT-2002"), NOW - timedelta(minutes=10), ACTOR, ROLE_A, PERMISSION,
        "ERR-KICAD-0146", "Berechtigung fehlt.", CorrelationId("COR-00002002"),
    ))
    repo.append(GlobalSecurityStaffingReleaseAttemptRecord(
        BusinessId("GSEC-ATT-2003"), NOW, None, ROLE_B, PERMISSION,
        "ERR-KICAD-0122", "Keine Verantwortung verfügbar.", CorrelationId("COR-00002003"),
    ))
    return GlobalSecurityStaffingReleaseAttemptSearchService(uow.connection)


def test_kombinierte_filter_und_freitext(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = seed(uow)
        page = service.search(GlobalSecurityStaffingReleaseAttemptSearchFilter(
            actor_id=ACTOR, acting_role=ROLE_A, reason_text="berechtigung"
        ))
        assert page.total_items == 1
        assert page.items[0].denial_code == "ERR-KICAD-0146"


def test_pagination_ist_stabil_und_neueste_zuerst(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = seed(uow)
        first = service.search(page=1, page_size=2)
        second = service.search(page=2, page_size=2)
        assert [str(item.attempt_id) for item in first.items] == ["GSEC-ATT-2003", "GSEC-ATT-2002"]
        assert [str(item.attempt_id) for item in second.items] == ["GSEC-ATT-2001"]
        assert first.has_next and second.has_previous


def test_diagnose_aggregiert_codes_rolllen_und_fehlende_person(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = seed(uow)
        diagnostic = service.diagnostic()
        assert diagnostic.total_attempts == 3
        assert diagnostic.distinct_actors == 1
        assert diagnostic.attempts_without_actor == 1
        assert diagnostic.distinct_roles == 2
        assert diagnostic.first_attempt_at == NOW - timedelta(minutes=20)
        assert diagnostic.latest_attempt_at == NOW
        assert diagnostic.top_roles[0] == (str(ROLE_A), 2)


def test_zeitraum_filtert_diagnose(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = seed(uow)
        diagnostic = service.diagnostic(GlobalSecurityStaffingReleaseAttemptSearchFilter(
            from_timestamp=NOW - timedelta(minutes=15)
        ))
        assert diagnostic.total_attempts == 2


def test_leere_diagnose_hat_definierte_nullwerte(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAttemptRepository(uow.connection)
        diagnostic = GlobalSecurityStaffingReleaseAttemptSearchService(uow.connection).diagnostic()
        assert diagnostic.total_attempts == 0
        assert diagnostic.first_attempt_at is None
        assert diagnostic.latest_attempt_at is None


def test_ungueltige_filter_und_pagination_werden_abgelehnt(tmp_path):
    with pytest.raises(ValueError, match="ERR-KICAD-0154"):
        GlobalSecurityStaffingReleaseAttemptSearchFilter(from_timestamp=datetime(2026, 8, 6))
    with pytest.raises(ValueError, match="ERR-KICAD-0155"):
        GlobalSecurityStaffingReleaseAttemptSearchFilter(
            from_timestamp=NOW, until_timestamp=NOW - timedelta(seconds=1)
        )
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteGlobalSecurityStaffingReleaseAttemptRepository(uow.connection)
        service = GlobalSecurityStaffingReleaseAttemptSearchService(uow.connection)
        with pytest.raises(ValueError, match="ERR-KICAD-0156"):
            service.search(page=0)
        with pytest.raises(ValueError, match="ERR-KICAD-0157"):
            service.search(page_size=201)
