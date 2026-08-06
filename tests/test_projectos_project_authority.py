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


def create_service(tmp_path) -> ProjectAuthorityService:
    database = tmp_path / "projectos.db"
    uow = SQLiteUnitOfWork(database)
    uow.__enter__()
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
    # Die Verbindung bleibt für die Lebensdauer des Services geöffnet.
    service = ProjectAuthorityService(responsibilities)
    object.__setattr__(service, "_test_uow", uow)
    return service


def test_projektleiter_hat_vorrang(tmp_path) -> None:
    result = create_service(tmp_path).resolve(PROJECT, at=NOW)
    assert result.authorized_user.user_id == LEADER
    assert result.source is ProjectResponsibilityType.PROJECT_LEADER


def test_stellvertretung_uebernimmt_bei_abwesenheit(tmp_path) -> None:
    result = create_service(tmp_path).resolve(
        PROJECT, at=NOW, unavailable_user_ids=frozenset({LEADER})
    )
    assert result.authorized_user.user_id == DEPUTY
    assert result.source is ProjectResponsibilityType.DEPUTY


def test_nachfolger_uebernimmt_nach_projektleiter_und_stellvertretung(tmp_path) -> None:
    result = create_service(tmp_path).resolve(
        PROJECT, at=NOW, unavailable_user_ids=frozenset({LEADER, DEPUTY})
    )
    assert result.authorized_user.user_id == SUCCESSOR
    assert result.source is ProjectResponsibilityType.SUCCESSOR


def test_vertrauensperson_wird_nicht_automatisch_handlungsberechtigt(tmp_path) -> None:
    service = create_service(tmp_path)
    with pytest.raises(LookupError, match="ERR-PRJ-0004"):
        service.resolve(
            PROJECT,
            at=NOW,
            unavailable_user_ids=frozenset({LEADER, DEPUTY, SUCCESSOR}),
        )


def test_pruefzeitpunkt_benoetigt_zeitzone(tmp_path) -> None:
    with pytest.raises(ValueError, match="Zeitzonenbezug"):
        create_service(tmp_path).resolve(PROJECT, at=datetime(2026, 8, 6, 8, 0))
