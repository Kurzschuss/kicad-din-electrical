"""Deterministische Ermittlung der handlungsberechtigten Projektperson."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .identifiers import BusinessId
from .identity_persistence import UserAccount
from .project_responsibilities import (
    ProjectResponsibilitySnapshot,
    ProjectResponsibilityType,
    SQLiteProjectResponsibilityRepository,
)


@dataclass(frozen=True, slots=True)
class ProjectAuthorityResolution:
    """Nachvollziehbares Ergebnis einer projektbezogenen Vertretungsentscheidung."""

    project_id: BusinessId
    resolved_at: datetime
    authorized_user: UserAccount
    source: ProjectResponsibilityType
    unavailable_user_ids: frozenset[BusinessId]
    reason: str

    def __post_init__(self) -> None:
        if self.resolved_at.tzinfo is None:
            raise ValueError("resolved_at benötigt einen Zeitzonenbezug.")
        object.__setattr__(self, "resolved_at", self.resolved_at.astimezone(timezone.utc))
        object.__setattr__(self, "unavailable_user_ids", frozenset(self.unavailable_user_ids))
        normalized = self.reason.strip()
        if not normalized:
            raise ValueError("Eine Vertretungsentscheidung benötigt eine Begründung.")
        object.__setattr__(self, "reason", normalized)


class ProjectAuthorityService:
    """Ermittelt die handlungsberechtigte Person nach verbindlicher Priorität."""

    _PRIORITY = (
        (ProjectResponsibilityType.PROJECT_LEADER, "project_leader"),
        (ProjectResponsibilityType.DEPUTY, "deputy"),
        (ProjectResponsibilityType.SUCCESSOR, "successor"),
    )

    def __init__(self, responsibilities: SQLiteProjectResponsibilityRepository) -> None:
        self._responsibilities = responsibilities

    def resolve(
        self,
        project_id: BusinessId,
        *,
        at: datetime,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> ProjectAuthorityResolution:
        if at.tzinfo is None:
            raise ValueError("Der Prüfzeitpunkt benötigt einen Zeitzonenbezug.")
        instant = at.astimezone(timezone.utc)
        unavailable = frozenset(unavailable_user_ids)
        snapshot = self._responsibilities.snapshot(project_id, at=instant)

        for responsibility, attribute in self._PRIORITY:
            user = getattr(snapshot, attribute)
            if user is None or not user.active or user.user_id in unavailable:
                continue
            return ProjectAuthorityResolution(
                project_id=project_id,
                resolved_at=instant,
                authorized_user=user,
                source=responsibility,
                unavailable_user_ids=unavailable,
                reason=self._reason(responsibility),
            )

        raise LookupError(
            "ERR-PRJ-0004: Keine handlungsberechtigte Projektperson konnte ermittelt werden."
        )

    @staticmethod
    def _reason(responsibility: ProjectResponsibilityType) -> str:
        if responsibility is ProjectResponsibilityType.PROJECT_LEADER:
            return "Der aktive Projektleiter ist handlungsberechtigt."
        if responsibility is ProjectResponsibilityType.DEPUTY:
            return "Die aktive Stellvertretung übernimmt, weil der Projektleiter nicht verfügbar ist."
        return "Der aktive Nachfolger übernimmt, weil Projektleiter und Stellvertretung nicht verfügbar sind."
