"""Projektbezogene Handlungsvollmachten und Verbindung zur Autorisierung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .authorization import AuthorizationResult
from .identifiers import BusinessId
from .identity_persistence import SQLiteIdentityRepository
from .project_authority import ProjectAuthorityResolution, ProjectAuthorityService
from .project_responsibilities import ProjectResponsibilityType


@dataclass(frozen=True, slots=True)
class ProjectActionAuthorizationResult:
    """Nachvollziehbares Ergebnis einer projektbezogenen Autorisierung."""

    allowed: bool
    reason: str
    authority: ProjectAuthorityResolution
    permission: BusinessId
    project_grant_match: bool
    authorization: AuthorizationResult | None = None


class SQLiteProjectAuthorityPolicyRepository:
    """Speichert Berechtigungen, die einer Projektfunktion zugeordnet sind."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_project_authority_permissions (
                project_id TEXT NOT NULL,
                responsibility TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                PRIMARY KEY(project_id, responsibility, permission_id)
            )
            """
        )

    def set_permissions(
        self,
        project_id: BusinessId,
        responsibility: ProjectResponsibilityType,
        permissions: frozenset[BusinessId],
    ) -> None:
        """Ersetzt die vollständige Berechtigungsmenge einer Projektfunktion."""
        self._connection.execute(
            """
            DELETE FROM projectos_project_authority_permissions
            WHERE project_id = ? AND responsibility = ?
            """,
            (str(project_id), responsibility.value),
        )
        self._connection.executemany(
            """
            INSERT INTO projectos_project_authority_permissions(
                project_id, responsibility, permission_id
            ) VALUES (?, ?, ?)
            """,
            (
                (str(project_id), responsibility.value, str(permission))
                for permission in sorted(permissions, key=str)
            ),
        )

    def permissions_for(
        self,
        project_id: BusinessId,
        responsibility: ProjectResponsibilityType,
    ) -> frozenset[BusinessId]:
        rows = self._connection.execute(
            """
            SELECT permission_id FROM projectos_project_authority_permissions
            WHERE project_id = ? AND responsibility = ?
            ORDER BY permission_id
            """,
            (str(project_id), responsibility.value),
        ).fetchall()
        return frozenset(BusinessId.parse(row["permission_id"]) for row in rows)

    def grants(
        self,
        project_id: BusinessId,
        responsibility: ProjectResponsibilityType,
        permission: BusinessId,
    ) -> bool:
        row = self._connection.execute(
            """
            SELECT 1 FROM projectos_project_authority_permissions
            WHERE project_id = ? AND responsibility = ? AND permission_id = ?
            """,
            (str(project_id), responsibility.value, str(permission)),
        ).fetchone()
        return row is not None


class ProjectActionAuthorizationService:
    """Verbindet Projektvertretung, Handlungsvollmacht und Benutzerautorisierung."""

    def __init__(
        self,
        authority: ProjectAuthorityService,
        policies: SQLiteProjectAuthorityPolicyRepository,
        identities: SQLiteIdentityRepository,
    ) -> None:
        self._authority = authority
        self._policies = policies
        self._identities = identities

    def authorize(
        self,
        project_id: BusinessId,
        permission: BusinessId,
        *,
        at: datetime,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> ProjectActionAuthorizationResult:
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt einen Zeitzonenbezug.")
        instant = at.astimezone(timezone.utc)
        authority = self._authority.resolve(
            project_id,
            at=instant,
            unavailable_user_ids=unavailable_user_ids,
        )

        project_grant = self._policies.grants(project_id, authority.source, permission)
        if not project_grant:
            return ProjectActionAuthorizationResult(
                allowed=False,
                reason="Die ermittelte Projektfunktion besitzt keine Handlungsvollmacht für diese Berechtigung.",
                authority=authority,
                permission=permission,
                project_grant_match=False,
            )

        context = self._identities.create_context(
            authority.authorized_user.user_id,
            project_id=project_id,
        )
        authorization = self._identities.create_authorization_service().authorize(
            context,
            permission,
            at=instant,
        )
        return ProjectActionAuthorizationResult(
            allowed=authorization.allowed,
            reason=(
                "Projektfunktion und Benutzerautorisierung erlauben die Handlung."
                if authorization.allowed
                else f"Die Projektfunktion ist bevollmächtigt, aber die Benutzerautorisierung lehnt ab: {authorization.reason}"
            ),
            authority=authority,
            permission=permission,
            project_grant_match=True,
            authorization=authorization,
        )
