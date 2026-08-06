"""Autorisierung globaler Sicherheitsbesetzungs-Freigabeentscheidungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .authorization import AuthorizationResult
from .identifiers import BusinessId, CorrelationId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import (
    GlobalSecurityAuthorityResolution,
    SQLiteGlobalSecurityResponsibilityRepository,
)
from .kicad_global_security_quality_gate import GlobalSecurityStaffingGateResult
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
    """Verbindet globale Verantwortung, Rollenrecht und Freigabeaudit."""

    def __init__(
        self,
        responsibilities: SQLiteGlobalSecurityResponsibilityRepository,
        identities: SQLiteIdentityRepository,
        releases: SQLiteGlobalSecurityStaffingReleaseRepository,
    ) -> None:
        self._responsibilities = responsibilities
        self._identities = identities
        self._releases = releases

    def decide(
        self,
        *,
        release_id: BusinessId,
        gate_result: GlobalSecurityStaffingGateResult,
        decided_at: datetime,
        acting_role: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> AuthorizedGlobalSecurityStaffingReleaseDecision:
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0142: Der Freigabezeitpunkt benötigt eine Zeitzone.")
        instant = decided_at.astimezone(timezone.utc)
        authority = self._responsibilities.resolve(
            at=instant,
            unavailable_user_ids=unavailable_user_ids,
        )
        context = self._identities.create_context(authority.user.user_id)
        authorization = self._identities.create_authorization_service().authorize(
            context,
            PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE,
            at=instant,
        )
        if not authorization.allowed:
            raise PermissionError(f"ERR-KICAD-0146: {authorization.reason}")
        if acting_role not in authorization.matched_roles:
            raise PermissionError(
                "ERR-KICAD-0147: Die handelnde Rolle erteilt die globale Besetzungsfreigabe nicht."
            )
        record = self._releases.append(
            release_id=release_id,
            gate_result=gate_result,
            decided_at=instant,
            actor_id=authority.user.user_id,
            acting_role=acting_role,
            reason=reason,
            correlation_id=correlation_id,
        )
        return AuthorizedGlobalSecurityStaffingReleaseDecision(
            authority,
            authorization,
            record,
        )
