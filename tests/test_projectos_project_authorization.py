from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    ProjectActionAuthorizationService,
    ProjectAuthorityService,
    ProjectResponsibility,
    ProjectResponsibilityType,
    Role,
    SQLiteIdentityRepository,
    SQLiteProjectAuthorityPolicyRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
PERMISSION = BusinessId("PERM-PROJECT-APPROVE")
ROLE = BusinessId("ROLE-PROJECT-MANAGEMENT")
LEADER = BusinessId("USR-LEADER")
DEPUTY = BusinessId("USR-DEPUTY")


def configure(uow: SQLiteUnitOfWork, *, blacklist_leader: bool = False):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(LEADER, "Projektleitung"))
    identities.upsert_user(UserAccount(DEPUTY, "Stellvertretung"))
    identities.upsert_role(Role(ROLE, frozenset({PERMISSION})))
    identities.assign_role(LEADER, ROLE)
    identities.assign_role(DEPUTY, ROLE)
    if blacklist_leader:
        identities.set_blacklist(LEADER, frozenset({PERMISSION}))

    responsibilities = SQLiteProjectResponsibilityRepository(uow.connection, identities)
    responsibilities.assign(
        ProjectResponsibility(
            PROJECT,
            ProjectResponsibilityType.PROJECT_LEADER,
            LEADER,
            NOW,
            reason="Projektleitung",
        )
    )
    responsibilities.assign(
        ProjectResponsibility(
            PROJECT,
            ProjectResponsibilityType.DEPUTY,
            DEPUTY,
            NOW,
            reason="Vertretung",
        )
    )
    policies = SQLiteProjectAuthorityPolicyRepository(uow.connection)
    policies.set_permissions(
        PROJECT,
        ProjectResponsibilityType.PROJECT_LEADER,
        frozenset({PERMISSION}),
    )
    policies.set_permissions(
        PROJECT,
        ProjectResponsibilityType.DEPUTY,
        frozenset({PERMISSION}),
    )
    return ProjectActionAuthorizationService(
        ProjectAuthorityService(responsibilities), policies, identities
    ), policies


def test_projektleiter_wird_mit_beiden_pruefebenen_autorisiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _ = configure(uow)
        result = service.authorize(PROJECT, PERMISSION, at=NOW)
        assert result.allowed
        assert result.project_grant_match
        assert result.authority.authorized_user.user_id == LEADER
        assert result.authorization is not None and result.authorization.allowed


def test_stellvertretung_wird_bei_abwesenheit_autorisiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _ = configure(uow)
        result = service.authorize(
            PROJECT,
            PERMISSION,
            at=NOW,
            unavailable_user_ids=frozenset({LEADER}),
        )
        assert result.allowed
        assert result.authority.source is ProjectResponsibilityType.DEPUTY
        assert result.authority.authorized_user.user_id == DEPUTY


def test_fehlende_projektvollmacht_lehnt_vor_benutzerautorisierung_ab(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, policies = configure(uow)
        policies.set_permissions(PROJECT, ProjectResponsibilityType.PROJECT_LEADER, frozenset())
        result = service.authorize(PROJECT, PERMISSION, at=NOW)
        assert not result.allowed
        assert not result.project_grant_match
        assert result.authorization is None


def test_blacklist_bleibt_auch_bei_projektvollmacht_vorrangig(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _ = configure(uow, blacklist_leader=True)
        result = service.authorize(PROJECT, PERMISSION, at=NOW)
        assert not result.allowed
        assert result.project_grant_match
        assert result.authorization is not None
        assert result.authorization.blacklist_match


def test_pruefzeitpunkt_benoetigt_zeitzone(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _ = configure(uow)
        with pytest.raises(ValueError, match="Zeitzonenbezug"):
            service.authorize(PROJECT, PERMISSION, at=datetime(2026, 8, 6, 9, 0))
