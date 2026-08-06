from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    AuthorizationService,
    BusinessId,
    ExceptionRight,
    Role,
    SQLiteIdentityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)


NOW = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
USER = BusinessId("USR-0001")
ROLE = BusinessId("ROLE-ENGINEER")
PERMISSION = BusinessId("PERM-DEVICE-WRITE")


def test_benutzer_rolle_und_berechtigung_bleiben_persistent(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with SQLiteUnitOfWork(database) as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Uwe Zimprich"))
        identities.upsert_role(Role(ROLE, frozenset({PERMISSION})))
        identities.assign_role(USER, ROLE)

    with SQLiteUnitOfWork(database) as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        context = identities.create_context(USER)
        service = identities.create_authorization_service()
        decision = service.authorize(context, PERMISSION, at=NOW)
        assert decision.allowed
        assert decision.matched_roles == (ROLE,)


def test_blacklist_hat_auch_persistent_vorrang_vor_rolle(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Testbenutzer"))
        identities.upsert_role(Role(ROLE, frozenset({PERMISSION})))
        identities.assign_role(USER, ROLE)
        identities.set_blacklist(USER, frozenset({PERMISSION}))
        decision = identities.create_authorization_service().authorize(
            identities.create_context(USER), PERMISSION, at=NOW
        )
        assert not decision.allowed
        assert decision.blacklist_match


def test_whitelist_und_ausnahmerecht_werden_geladen(tmp_path) -> None:
    whitelist_permission = BusinessId("PERM-WHITELIST")
    exception_permission = BusinessId("PERM-EXCEPTION")
    project_id = BusinessId("PRJ-0001")
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Testbenutzer"))
        identities.set_whitelist(USER, frozenset({whitelist_permission}))
        identities.add_exception_right(
            ExceptionRight(
                BusinessId("EXC-0001"), USER, exception_permission,
                NOW - timedelta(minutes=1), NOW + timedelta(minutes=1),
                "Temporäre Freigabe", project_id,
            )
        )
        service = identities.create_authorization_service()
        context = identities.create_context(USER, project_id=project_id)
        assert service.authorize(context, whitelist_permission, at=NOW).whitelist_match
        assert service.authorize(context, exception_permission, at=NOW).matched_exception == BusinessId("EXC-0001")


def test_deaktivierter_benutzer_erhaelt_keinen_kontext(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Gesperrt", active=False))
        with pytest.raises(PermissionError, match="ERR-IDM-0002"):
            identities.create_context(USER)


def test_unbekannte_rollenzuordnung_wird_abgewiesen(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Testbenutzer"))
        with pytest.raises(LookupError, match="ERR-IDM-0003"):
            identities.assign_role(USER, ROLE)


def test_rollenaenderung_ersetzt_alte_berechtigungen(tmp_path) -> None:
    old_permission = BusinessId("PERM-OLD")
    new_permission = BusinessId("PERM-NEW")
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        identities = SQLiteIdentityRepository(uow.connection)
        identities.upsert_user(UserAccount(USER, "Testbenutzer"))
        identities.upsert_role(Role(ROLE, frozenset({old_permission})))
        identities.assign_role(USER, ROLE)
        identities.upsert_role(Role(ROLE, frozenset({new_permission})))
        service: AuthorizationService = identities.create_authorization_service()
        context = identities.create_context(USER)
        assert not service.authorize(context, old_permission, at=NOW).allowed
        assert service.authorize(context, new_permission, at=NOW).allowed
