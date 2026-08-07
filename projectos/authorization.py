"""Rollen- und Berechtigungsprüfung für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

from .identifiers import BusinessId


@dataclass(frozen=True, slots=True)
class Role:
    """Rolle mit einer unveränderlichen Menge von Berechtigungen."""

    role_id: BusinessId
    permissions: frozenset[BusinessId] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        object.__setattr__(self, "permissions", frozenset(self.permissions))


@dataclass(frozen=True, slots=True)
class ExceptionRight:
    """Zeitlich und sachlich begrenztes Ausnahmerecht."""

    exception_id: BusinessId
    user_id: BusinessId
    permission: BusinessId
    valid_from: datetime
    valid_until: datetime
    reason: str
    project_id: BusinessId | None = None

    def __post_init__(self) -> None:
        if self.valid_from.tzinfo is None or self.valid_until.tzinfo is None:
            raise ValueError("Ausnahmerechte benötigen Zeitzoneninformationen.")
        valid_from = self.valid_from.astimezone(timezone.utc)
        valid_until = self.valid_until.astimezone(timezone.utc)
        if valid_until <= valid_from:
            raise ValueError("Das Ende eines Ausnahmerechts muss nach dem Beginn liegen.")
        reason = self.reason.strip()
        if not reason:
            raise ValueError("Ein Ausnahmerecht benötigt eine Begründung.")
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        object.__setattr__(self, "reason", reason)

    def is_active(self, at: datetime, project_id: BusinessId | None) -> bool:
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt eine Zeitzone.")
        instant = at.astimezone(timezone.utc)
        project_matches = self.project_id is None or self.project_id == project_id
        return self.valid_from <= instant < self.valid_until and project_matches


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Unveränderlicher Kontext einer Berechtigungsentscheidung."""

    user_id: BusinessId
    role_ids: frozenset[BusinessId]
    project_id: BusinessId | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "role_ids", frozenset(self.role_ids))


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    """Nachvollziehbares Ergebnis einer Berechtigungsprüfung."""

    allowed: bool
    reason: str
    matched_roles: tuple[BusinessId, ...] = ()
    matched_exception: BusinessId | None = None
    whitelist_match: bool = False
    blacklist_match: bool = False


class AuthorizationService:
    """Deterministische Berechtigungsprüfung mit Sperrvorrang."""

    def __init__(
        self,
        *,
        roles: Mapping[BusinessId, Role] | None = None,
        whitelist: Mapping[BusinessId, frozenset[BusinessId]] | None = None,
        blacklist: Mapping[BusinessId, frozenset[BusinessId]] | None = None,
        exception_rights: tuple[ExceptionRight, ...] = (),
    ) -> None:
        self._roles = MappingProxyType(dict(roles or {}))
        self._whitelist = MappingProxyType(
            {user: frozenset(values) for user, values in (whitelist or {}).items()}
        )
        self._blacklist = MappingProxyType(
            {user: frozenset(values) for user, values in (blacklist or {}).items()}
        )
        self._exception_rights = tuple(exception_rights)

    def authorize(
        self,
        context: AuthorizationContext,
        permission: BusinessId,
        *,
        at: datetime,
    ) -> AuthorizationResult:
        """Prüft Blacklist, Rollen, Whitelist und Ausnahmerechte in fester Reihenfolge."""
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt eine Zeitzone.")

        denied = self._blacklist.get(context.user_id, frozenset())
        if permission in denied:
            return AuthorizationResult(
                False,
                "Die Berechtigung ist für den Benutzer ausdrücklich gesperrt.",
                blacklist_match=True,
            )

        matched_roles = tuple(
            role_id
            for role_id in sorted(context.role_ids, key=str)
            if role_id in self._roles and permission in self._roles[role_id].permissions
        )
        if matched_roles:
            return AuthorizationResult(
                True,
                "Die Berechtigung wurde durch eine Rolle erteilt.",
                matched_roles=matched_roles,
            )

        allowed = self._whitelist.get(context.user_id, frozenset())
        if permission in allowed:
            return AuthorizationResult(
                True,
                "Die Berechtigung wurde durch die Whitelist erteilt.",
                whitelist_match=True,
            )

        for right in self._exception_rights:
            if (
                right.user_id == context.user_id
                and right.permission == permission
                and right.is_active(at, context.project_id)
            ):
                return AuthorizationResult(
                    True,
                    "Die Berechtigung wurde durch ein aktives Ausnahmerecht erteilt.",
                    matched_exception=right.exception_id,
                )

        return AuthorizationResult(False, "Keine wirksame Berechtigung gefunden.")
