from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    ProjectAuthorityService,
    ProjectResponsibility,
    ProjectResponsibilityType,
    SQLiteIdentityRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
LEADER = BusinessId("USR-LEADER")
DEPUTY = BusinessId("USR-DEPUTY")
TRUSTED = BusinessId("USR-TRUSTED")
SUCCESSOR = BusinessId("USR-SUCCESSOR")


@pytest.fixture
def service(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        for user_id, name in (
            (LEADER, "Projektleitung"),
            (DEPUTY, "Stellvertretung"),
            (TRUSTED, "Vertrauensperson"),
            (SUCCESSOR, "Nachfolge"),
        ):
            identities.upsert_user(UserAccount(user_id, name))
        responsibilities = SQLiteProjectResponsibilityRepository(uow.connection, identities)
        for kind, user_id in (
            (ProjectResponsibilityType.PROJECT_LEADER, LEADER),
            (ProjectResponsibilityType.DEPUTY, DEPUTY),
            (ProjectResponsibilityType.TRUSTED_PERSON, TRUSTED),
            (ProjectResponsibilityType.SUCCESSOR, SUCCESSOR),
        ):
            responsibilities.assign(
                ProjectResponsibility(PROJECT, kind, user_id, NOW, reason="Testzuordnung")
            )
        yield ProjectAuthorityService(responsibilities)


def test_projektleiter_hat_vorrang(service) -> None:
    result = service.resolve(PROJECT, at=NOW)
    assert result.authorized_user.user_id == LEADER
    assert result.source is ProjectResponsibilityType.PROJECT_LEADER


def test_stellvertretung_uebernimmt_bei_abwesenheit(service) -> None:
    result = service.resolve(PROJECT, at=NOW, unavailable_user_ids=frozenset({LEADER}))
    assert result.authorized_user.user_id == DEPUTY
    assert result.source is ProjectResponsibilityType.DEPUTY


def test_nachfolger_uebernimmt_nach_projektleiter_und_stellvertretung(service) -> None:
    result = service.resolve(
        PROJECT, at=NOW, unavailable_user_ids=frozenset({LEADER, DEPUTY})
    )
    assert result.authorized_user.user_id == SUCCESSOR
    assert result.source is ProjectResponsibilityType.SUCCESSOR


def test_vertrauensperson_wird_nicht_automatisch_handlungsberechtigt(service) -> None:
    with pytest.raises(LookupError, match="ERR-PRJ-0004"):
        service.resolve(
            PROJECT,
            at=NOW,
            unavailable_user_ids=frozenset({LEADER, DEPUTY, SUCCESSOR}),
        )


def test_pruefzeitpunkt_benoetigt_zeitzone(service) -> None:
    with pytest.raises(ValueError, match="Zeitzonenbezug"):
        service.resolve(PROJECT, at=datetime(2026, 8, 6, 8, 0))
