from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    ProjectResponsibility,
    ProjectResponsibilityType,
    SQLiteIdentityRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)


def test_projektverantwortungen_werden_persistiert_und_aufgeloest(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    now = datetime(2026, 8, 6, 8, tzinfo=timezone.utc)
    users = {
        ProjectResponsibilityType.PROJECT_LEADER: UserAccount(BusinessId("USR-LEADER"), "Projektleiter"),
        ProjectResponsibilityType.DEPUTY: UserAccount(BusinessId("USR-DEPUTY"), "Stellvertretung"),
        ProjectResponsibilityType.TRUSTED_PERSON: UserAccount(BusinessId("USR-TRUST"), "Vertrauensperson"),
        ProjectResponsibilityType.SUCCESSOR: UserAccount(BusinessId("USR-SUCCESSOR"), "Nachfolger"),
    }
    project_id = BusinessId("PRJ-0001")
    with SQLiteUnitOfWork(database) as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        repository = SQLiteProjectResponsibilityRepository(uow.connection, identities)
        for kind, user in users.items():
            identities.upsert_user(user)
            repository.assign(ProjectResponsibility(project_id, kind, user.user_id, now, reason="Projektbesetzung"))

    with SQLiteUnitOfWork(database) as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        snapshot = SQLiteProjectResponsibilityRepository(uow.connection, identities).snapshot(project_id, at=now)
        assert snapshot.project_leader == users[ProjectResponsibilityType.PROJECT_LEADER]
        assert snapshot.deputy == users[ProjectResponsibilityType.DEPUTY]
        assert snapshot.trusted_person == users[ProjectResponsibilityType.TRUSTED_PERSON]
        assert snapshot.successor == users[ProjectResponsibilityType.SUCCESSOR]


def test_ueberlappende_zuordnungen_werden_abgewiesen(tmp_path) -> None:
    now = datetime(2026, 8, 6, 8, tzinfo=timezone.utc)
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(BusinessId("USR-1"), "Erste Person"))
        identities.upsert_user(UserAccount(BusinessId("USR-2"), "Zweite Person"))
        repository = SQLiteProjectResponsibilityRepository(uow.connection, identities)
        repository.assign(ProjectResponsibility(
            BusinessId("PRJ-0001"), ProjectResponsibilityType.PROJECT_LEADER,
            BusinessId("USR-1"), now, now + timedelta(days=10), "Erste Besetzung",
        ))
        with pytest.raises(ValueError, match="ERR-PRJ-0003"):
            repository.assign(ProjectResponsibility(
                BusinessId("PRJ-0001"), ProjectResponsibilityType.PROJECT_LEADER,
                BusinessId("USR-2"), now + timedelta(days=5), None, "Überlappende Besetzung",
            ))


def test_aufeinanderfolgende_zuordnungen_sind_zulaessig(tmp_path) -> None:
    now = datetime(2026, 8, 6, 8, tzinfo=timezone.utc)
    change = now + timedelta(days=10)
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(BusinessId("USR-1"), "Erste Person"))
        identities.upsert_user(UserAccount(BusinessId("USR-2"), "Zweite Person"))
        repository = SQLiteProjectResponsibilityRepository(uow.connection, identities)
        repository.assign(ProjectResponsibility(
            BusinessId("PRJ-0001"), ProjectResponsibilityType.PROJECT_LEADER,
            BusinessId("USR-1"), now, change, "Bis zum Wechsel",
        ))
        repository.assign(ProjectResponsibility(
            BusinessId("PRJ-0001"), ProjectResponsibilityType.PROJECT_LEADER,
            BusinessId("USR-2"), change, None, "Nach dem Wechsel",
        ))
        assert repository.active_assignment(
            BusinessId("PRJ-0001"), ProjectResponsibilityType.PROJECT_LEADER, at=change
        ).user_id == BusinessId("USR-2")


def test_deaktivierte_benutzer_koennen_nicht_zugeordnet_werden(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(BusinessId("USR-INACTIVE"), "Inaktiv", active=False))
        repository = SQLiteProjectResponsibilityRepository(uow.connection, identities)
        with pytest.raises(PermissionError, match="ERR-PRJ-0002"):
            repository.assign(ProjectResponsibility(
                BusinessId("PRJ-0001"), ProjectResponsibilityType.DEPUTY,
                BusinessId("USR-INACTIVE"), datetime.now(timezone.utc), reason="Nicht zulässig",
            ))
