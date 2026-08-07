"""Persistente projektbezogene Verantwortungen für ProjectOS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3

from .identifiers import BusinessId
from .identity_persistence import SQLiteIdentityRepository, UserAccount


class ProjectResponsibilityType(StrEnum):
    PROJECT_LEADER = "PROJECT_LEADER"
    DEPUTY = "DEPUTY"
    TRUSTED_PERSON = "TRUSTED_PERSON"
    SUCCESSOR = "SUCCESSOR"


@dataclass(frozen=True, slots=True)
class ProjectResponsibility:
    project_id: BusinessId
    responsibility: ProjectResponsibilityType
    user_id: BusinessId
    valid_from: datetime
    valid_until: datetime | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if self.valid_from.tzinfo is None:
            raise ValueError("valid_from benötigt einen Zeitzonenbezug.")
        valid_from = self.valid_from.astimezone(timezone.utc)
        valid_until = self.valid_until
        if valid_until is not None:
            if valid_until.tzinfo is None:
                raise ValueError("valid_until benötigt einen Zeitzonenbezug.")
            valid_until = valid_until.astimezone(timezone.utc)
            if valid_until <= valid_from:
                raise ValueError("valid_until muss nach valid_from liegen.")
        reason = self.reason.strip()
        if not reason:
            raise ValueError("Eine Projektverantwortung benötigt eine Begründung.")
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        object.__setattr__(self, "reason", reason)

    def is_active(self, at: datetime) -> bool:
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt einen Zeitzonenbezug.")
        instant = at.astimezone(timezone.utc)
        return self.valid_from <= instant and (self.valid_until is None or instant < self.valid_until)


@dataclass(frozen=True, slots=True)
class ProjectResponsibilitySnapshot:
    project_id: BusinessId
    project_leader: UserAccount | None
    deputy: UserAccount | None
    trusted_person: UserAccount | None
    successor: UserAccount | None


class SQLiteProjectResponsibilityRepository:
    """Speichert eindeutige, zeitlich gültige Projektfunktionen in SQLite."""

    def __init__(self, connection: sqlite3.Connection, identities: SQLiteIdentityRepository) -> None:
        self._connection = connection
        self._identities = identities
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_project_responsibilities (
                project_id TEXT NOT NULL,
                responsibility TEXT NOT NULL,
                user_id TEXT NOT NULL,
                valid_from TEXT NOT NULL,
                valid_until TEXT,
                reason TEXT NOT NULL,
                PRIMARY KEY(project_id, responsibility, valid_from),
                FOREIGN KEY(user_id) REFERENCES projectos_users(user_id) ON DELETE RESTRICT
            )
            """
        )

    def assign(self, assignment: ProjectResponsibility) -> ProjectResponsibility:
        user = self._identities.get_user(assignment.user_id)
        if user is None:
            raise LookupError("ERR-PRJ-0001: Benutzer wurde nicht gefunden.")
        if not user.active:
            raise PermissionError("ERR-PRJ-0002: Benutzer ist deaktiviert.")
        overlaps = self._connection.execute(
            """
            SELECT 1 FROM projectos_project_responsibilities
            WHERE project_id = ? AND responsibility = ?
              AND (? IS NULL OR valid_from < ?)
              AND (valid_until IS NULL OR valid_until > ?)
            LIMIT 1
            """,
            (
                str(assignment.project_id), assignment.responsibility.value,
                None if assignment.valid_until is None else assignment.valid_until.isoformat(),
                None if assignment.valid_until is None else assignment.valid_until.isoformat(),
                assignment.valid_from.isoformat(),
            ),
        ).fetchone()
        if overlaps is not None:
            raise ValueError("ERR-PRJ-0003: Für diese Projektfunktion existiert bereits eine überlappende Zuordnung.")
        self._connection.execute(
            """
            INSERT INTO projectos_project_responsibilities(
                project_id, responsibility, user_id, valid_from, valid_until, reason
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(assignment.project_id), assignment.responsibility.value, str(assignment.user_id),
                assignment.valid_from.isoformat(),
                None if assignment.valid_until is None else assignment.valid_until.isoformat(),
                assignment.reason,
            ),
        )
        return assignment

    def active_assignment(
        self, project_id: BusinessId, responsibility: ProjectResponsibilityType, *, at: datetime
    ) -> ProjectResponsibility | None:
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt einen Zeitzonenbezug.")
        instant = at.astimezone(timezone.utc).isoformat()
        row = self._connection.execute(
            """
            SELECT * FROM projectos_project_responsibilities
            WHERE project_id = ? AND responsibility = ?
              AND valid_from <= ? AND (valid_until IS NULL OR valid_until > ?)
            ORDER BY valid_from DESC LIMIT 1
            """,
            (str(project_id), responsibility.value, instant, instant),
        ).fetchone()
        return None if row is None else self._decode(row)

    def snapshot(self, project_id: BusinessId, *, at: datetime) -> ProjectResponsibilitySnapshot:
        def user_for(kind: ProjectResponsibilityType) -> UserAccount | None:
            assignment = self.active_assignment(project_id, kind, at=at)
            return None if assignment is None else self._identities.get_user(assignment.user_id)

        return ProjectResponsibilitySnapshot(
            project_id=project_id,
            project_leader=user_for(ProjectResponsibilityType.PROJECT_LEADER),
            deputy=user_for(ProjectResponsibilityType.DEPUTY),
            trusted_person=user_for(ProjectResponsibilityType.TRUSTED_PERSON),
            successor=user_for(ProjectResponsibilityType.SUCCESSOR),
        )

    def all_for_project(self, project_id: BusinessId) -> tuple[ProjectResponsibility, ...]:
        rows = self._connection.execute(
            """
            SELECT * FROM projectos_project_responsibilities
            WHERE project_id = ? ORDER BY responsibility, valid_from
            """,
            (str(project_id),),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    @staticmethod
    def _decode(row: sqlite3.Row) -> ProjectResponsibility:
        return ProjectResponsibility(
            project_id=BusinessId.parse(row["project_id"]),
            responsibility=ProjectResponsibilityType(row["responsibility"]),
            user_id=BusinessId.parse(row["user_id"]),
            valid_from=datetime.fromisoformat(row["valid_from"]),
            valid_until=None if row["valid_until"] is None else datetime.fromisoformat(row["valid_until"]),
            reason=row["reason"],
        )
