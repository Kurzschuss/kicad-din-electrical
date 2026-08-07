"""Projektbezogene Autorisierung und persistente Protokollierung von KiCad-Freigaben."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .identifiers import BusinessId, CorrelationId
from .kicad_quality_gate import KiCadQualityGateResult
from .kicad_release_attempt_audit import SQLiteKiCadReleaseAttemptAuditRepository
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
        attempt_audit: SQLiteKiCadReleaseAttemptAuditRepository | None = None,
    ) -> None:
        self._authorization = authorization
        self._audit = audit
        self._attempt_audit = attempt_audit

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
        attempt_id: BusinessId | None = None,
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
        actor_id = authorization.authority.authorized_user.user_id
        if not authorization.allowed:
            self._audit_denial(
                attempt_id=attempt_id,
                project_id=gate_result.project_id,
                attempted_at=instant,
                actor_id=actor_id,
                acting_role=acting_role,
                correlation_id=correlation_id,
                denial_code="ERR-KICAD-0078",
                denial_reason=authorization.reason,
            )
            raise PermissionError(f"ERR-KICAD-0078: {authorization.reason}")
        user_authorization = authorization.authorization
        if user_authorization is None or acting_role not in user_authorization.matched_roles:
            denial_reason = "Die handelnde Rolle erteilt die KiCad-Freigabeberechtigung nicht."
            self._audit_denial(
                attempt_id=attempt_id,
                project_id=gate_result.project_id,
                attempted_at=instant,
                actor_id=actor_id,
                acting_role=acting_role,
                correlation_id=correlation_id,
                denial_code="ERR-KICAD-0079",
                denial_reason=denial_reason,
            )
            raise PermissionError(f"ERR-KICAD-0079: {denial_reason}")

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

    def _audit_denial(
        self,
        *,
        attempt_id: BusinessId | None,
        project_id: BusinessId,
        attempted_at: datetime,
        actor_id: BusinessId,
        acting_role: BusinessId,
        correlation_id: CorrelationId,
        denial_code: str,
        denial_reason: str,
    ) -> None:
        if self._attempt_audit is None:
            return
        if attempt_id is None:
            raise ValueError(
                "ERR-KICAD-0085: Bei aktiviertem Versuchsaudit benötigt ein abgelehnter Freigabeversuch eine Kennung."
            )
        self._attempt_audit.append(
            attempt_id=attempt_id,
            project_id=project_id,
            attempted_at=attempted_at,
            actor_id=actor_id,
            acting_role=acting_role,
            permission_id=PERM_KICAD_RELEASE_DECIDE,
            denial_code=denial_code,
            denial_reason=denial_reason,
            correlation_id=correlation_id,
        )
