"""Autorisierung globaler Sicherheitsbesetzungs-Freigabeentscheidungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import GlobalSecurityAuthorityResolution, SQLiteGlobalSecurityResponsibilityRepository
from .kicad_global_security_quality_gate import GlobalSecurityStaffingGateResult
from .kicad_global_security_release_attempt_audit import (
    GlobalSecurityStaffingReleaseAttemptRecord,
    SQLiteGlobalSecurityStaffingReleaseAttemptRepository,
)
from .kicad_global_security_release_audit import (
    GlobalSecurityStaffingReleaseRecord,
    SQLiteGlobalSecurityStaffingReleaseRepository,
)

PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE = BusinessId(
    "PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-DECIDE"
)


@dataclass(frozen=True, slots=True)
class AuthorizedGlobalSecurityStaffingReleaseDecision:
    authority: GlobalSecurityAuthorityResolution
    authorization: AuthorizationResult
    release_record: GlobalSecurityStaffingReleaseRecord


class AuthorizedGlobalSecurityStaffingReleaseService:
    """Verbindet globale Verantwortung, Rollenrecht, Freigabe- und Versuchsaudit."""

    def __init__(self, responsibilities: SQLiteGlobalSecurityResponsibilityRepository,
                 identities: SQLiteIdentityRepository,
                 releases: SQLiteGlobalSecurityStaffingReleaseRepository,
                 attempt_audit: SQLiteGlobalSecurityStaffingReleaseAttemptRepository | None = None) -> None:
        self._responsibilities = responsibilities
        self._identities = identities
        self._releases = releases
        self._attempt_audit = attempt_audit

    def decide(self, *, release_id: BusinessId, gate_result: GlobalSecurityStaffingGateResult,
               decided_at: datetime, acting_role: BusinessId, reason: str,
               correlation_id: CorrelationId,
               unavailable_user_ids: frozenset[BusinessId] = frozenset(),
               attempt_id: BusinessId | None = None) -> AuthorizedGlobalSecurityStaffingReleaseDecision:
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0142: Der Freigabezeitpunkt benötigt eine Zeitzone.")
        instant = decided_at.astimezone(timezone.utc)
        authority: GlobalSecurityAuthorityResolution | None = None
        try:
            authority = self._responsibilities.resolve(at=instant, unavailable_user_ids=unavailable_user_ids)
            context = self._identities.create_context(authority.user.user_id)
            authorization = self._identities.create_authorization_service().authorize(
                context, PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE, at=instant
            )
            if not authorization.allowed:
                raise PermissionError(f"ERR-KICAD-0146: {authorization.reason}")
            if acting_role not in authorization.matched_roles:
                raise PermissionError(
                    "ERR-KICAD-0147: Die handelnde Rolle erteilt die globale Besetzungsfreigabe nicht."
                )
        except (LookupError, PermissionError) as exc:
            self._audit_denial(
                attempt_id=attempt_id, attempted_at=instant,
                actor_id=authority.user.user_id if authority else None,
                acting_role=acting_role, denial=exc, correlation_id=correlation_id,
            )
            raise
        record = self._releases.append(
            release_id=release_id, gate_result=gate_result, decided_at=instant,
            actor_id=authority.user.user_id, acting_role=acting_role,
            reason=reason, correlation_id=correlation_id,
        )
        return AuthorizedGlobalSecurityStaffingReleaseDecision(authority, authorization, record)

    def _audit_denial(self, *, attempt_id: BusinessId | None, attempted_at: datetime,
                      actor_id: BusinessId | None, acting_role: BusinessId,
                      denial: Exception, correlation_id: CorrelationId) -> None:
        if self._attempt_audit is None:
            return
        if attempt_id is None:
            raise ValueError("ERR-KICAD-0153: Bei aktiviertem Versuchsaudit fehlt die Versuchskennung.") from denial
        text = str(denial)
        code, _, message = text.partition(":")
        self._attempt_audit.append(GlobalSecurityStaffingReleaseAttemptRecord(
            attempt_id=attempt_id,
            attempted_at=attempted_at,
            actor_id=actor_id,
            acting_role=acting_role,
            permission_id=PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE,
            denial_code=code,
            denial_reason=message.strip() or text,
            correlation_id=correlation_id,
        ))
