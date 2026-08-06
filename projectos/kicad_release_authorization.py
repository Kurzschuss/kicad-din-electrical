"""Projektbezogene Autorisierung und persistente Protokollierung von KiCad-Freigaben."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .identifiers import BusinessId, CorrelationId
from .kicad_quality_gate import KiCadQualityGateResult
from .kicad_release_audit import KiCadReleaseAuditRecord, SQLiteKiCadReleaseAuditRepository
from .project_authorization import ProjectActionAuthorizationResult, ProjectActionAuthorizationService


PERM_KICAD_RELEASE_DECIDE = BusinessId("PERM-KICAD-RELEASE-DECIDE")


@dataclass(frozen=True, slots=True)
class AuthorizedKiCadReleaseDecision:
    """Ergebnis einer autorisierten und persistent protokollierten Freigabeentscheidung."""

    authorization: ProjectActionAuthorizationResult
    record: KiCadReleaseAuditRecord


class AuthorizedKiCadReleaseService:
    """Verbindet Projektvollmacht, Rollenberechtigung und Freigabeaudit."""

    def __init__(
        self,
        authorization: ProjectActionAuthorizationService,
        audit: SQLiteKiCadReleaseAuditRepository,
    ) -> None:
        self._authorization = authorization
        self._audit = audit

    def decide(
        self,
        *,
        release_decision_id: BusinessId,
        gate_result: KiCadQualityGateResult,
        decided_at: datetime,
        acting_role: BusinessId,
        correlation_id: CorrelationId,
        reason: str,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> AuthorizedKiCadReleaseDecision:
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0074: Der Entscheidungszeitpunkt benötigt eine Zeitzone.")
        instant = decided_at.astimezone(timezone.utc)
        authorization = self._authorization.authorize(
            gate_result.project_id,
            PERM_KICAD_RELEASE_DECIDE,
            at=instant,
            unavailable_user_ids=unavailable_user_ids,
        )
        if not authorization.allowed:
            raise PermissionError(f"ERR-KICAD-0078: {authorization.reason}")
        user_authorization = authorization.authorization
        if user_authorization is None or acting_role not in user_authorization.matched_roles:
            raise PermissionError(
                "ERR-KICAD-0079: Die handelnde Rolle erteilt die KiCad-Freigabeberechtigung nicht."
            )

        actor_id = authorization.authority.authorized_user.user_id
        record = self._audit.append(
            release_decision_id=release_decision_id,
            gate_result=gate_result,
            decided_at=instant,
            actor_id=actor_id,
            acting_role=acting_role,
            correlation_id=correlation_id,
            reason=reason,
        )
        return AuthorizedKiCadReleaseDecision(authorization, record)
