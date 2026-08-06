from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    AuthorizationContext,
    AuthorizationService,
    BusinessId,
    ExceptionRight,
    Role,
)


def bid(value: str) -> BusinessId:
    return BusinessId.parse(value)


def test_role_grants_permission() -> None:
    role = Role(bid("ROLE-ENGINEERING"), frozenset({bid("PERM-MCB-EDIT")}))
    service = AuthorizationService(roles={role.role_id: role})
    context = AuthorizationContext(bid("USR-000001"), frozenset({role.role_id}))

    result = service.authorize(
        context,
        bid("PERM-MCB-EDIT"),
        at=datetime.now(timezone.utc),
    )

    assert result.allowed is True
    assert result.matched_roles == (role.role_id,)


def test_blacklist_has_priority_over_role_and_whitelist() -> None:
    user = bid("USR-000001")
    permission = bid("PERM-MCB-RELEASE")
    role = Role(bid("ROLE-PROJEKTLEITER"), frozenset({permission}))
    service = AuthorizationService(
        roles={role.role_id: role},
        whitelist={user: frozenset({permission})},
        blacklist={user: frozenset({permission})},
    )
    context = AuthorizationContext(user, frozenset({role.role_id}))

    result = service.authorize(context, permission, at=datetime.now(timezone.utc))

    assert result.allowed is False
    assert result.blacklist_match is True


def test_whitelist_grants_permission_without_role() -> None:
    user = bid("USR-000002")
    permission = bid("PERM-RCCB-READ")
    service = AuthorizationService(whitelist={user: frozenset({permission})})

    result = service.authorize(
        AuthorizationContext(user, frozenset()),
        permission,
        at=datetime.now(timezone.utc),
    )

    assert result.allowed is True
    assert result.whitelist_match is True


def test_active_exception_right_grants_project_permission() -> None:
    now = datetime.now(timezone.utc)
    user = bid("USR-000003")
    permission = bid("PERM-PROJECT-APPROVE")
    project = bid("PRJ-000012")
    right = ExceptionRight(
        bid("EXC-000001"),
        user,
        permission,
        now - timedelta(minutes=1),
        now + timedelta(minutes=5),
        "Zeitlich begrenzte Vertretung",
        project,
    )
    service = AuthorizationService(exception_rights=(right,))

    result = service.authorize(
        AuthorizationContext(user, frozenset(), project),
        permission,
        at=now,
    )

    assert result.allowed is True
    assert result.matched_exception == right.exception_id


def test_expired_exception_right_does_not_grant_permission() -> None:
    now = datetime.now(timezone.utc)
    right = ExceptionRight(
        bid("EXC-000002"),
        bid("USR-000004"),
        bid("PERM-MCB-EDIT"),
        now - timedelta(hours=2),
        now - timedelta(hours=1),
        "Abgelaufene Vertretung",
    )
    service = AuthorizationService(exception_rights=(right,))

    result = service.authorize(
        AuthorizationContext(right.user_id, frozenset()),
        right.permission,
        at=now,
    )

    assert result.allowed is False


def test_exception_right_requires_valid_time_range() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        ExceptionRight(
            bid("EXC-000003"),
            bid("USR-000005"),
            bid("PERM-MCB-EDIT"),
            now,
            now,
            "Ungültiger Zeitraum",
        )


def test_authorize_requires_timezone() -> None:
    service = AuthorizationService()
    with pytest.raises(ValueError):
        service.authorize(
            AuthorizationContext(bid("USR-000006"), frozenset()),
            bid("PERM-MCB-READ"),
            at=datetime.now(),
        )
