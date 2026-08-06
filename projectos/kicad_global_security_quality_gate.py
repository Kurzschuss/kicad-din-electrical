"""Qualitäts- und Freigabeprüfung der globalen Sicherheitsbesetzung."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .kicad_global_security_history import (
    GlobalSecurityResponsibilityDiagnostic,
    GlobalSecurityResponsibilityHistoryService,
)


class GlobalSecurityStaffingDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingPolicy:
    require_primary: bool = True
    require_deputy: bool = True
    require_active_primary: bool = True
    require_active_deputy: bool = True
    require_distinct_users: bool = True
    minimum_history_entries: int = 0

    def __post_init__(self) -> None:
        if self.minimum_history_entries < 0:
            raise ValueError("ERR-KICAD-0135: Die Mindestanzahl historischer Wechsel darf nicht negativ sein.")


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingFinding:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingGateResult:
    decision: GlobalSecurityStaffingDecision
    diagnostic: GlobalSecurityResponsibilityDiagnostic
    findings: tuple[GlobalSecurityStaffingFinding, ...]

    @property
    def approved(self) -> bool:
        return self.decision is GlobalSecurityStaffingDecision.APPROVED


class GlobalSecurityStaffingQualityGate:
    """Bewertet die aktuelle Besetzung, ohne Verantwortungen zu verändern."""

    def __init__(self, history: GlobalSecurityResponsibilityHistoryService) -> None:
        self._history = history

    def evaluate(
        self,
        policy: GlobalSecurityStaffingPolicy | None = None,
    ) -> GlobalSecurityStaffingGateResult:
        policy = policy or GlobalSecurityStaffingPolicy()
        diagnostic = self._history.diagnostic()
        findings: list[GlobalSecurityStaffingFinding] = []

        if diagnostic.total_changes < policy.minimum_history_entries:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0136",
                f"Nur {diagnostic.total_changes} historisierte Wechsel; benötigt werden mindestens {policy.minimum_history_entries}.",
            ))
            return GlobalSecurityStaffingGateResult(
                GlobalSecurityStaffingDecision.INSUFFICIENT_DATA,
                diagnostic,
                tuple(findings),
            )

        if policy.require_primary and diagnostic.primary is None:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0137", "Die globale Hauptverantwortung ist nicht besetzt."
            ))
        if policy.require_deputy and diagnostic.deputy is None:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0138", "Die globale Sicherheitsstellvertretung ist nicht besetzt."
            ))
        if policy.require_active_primary and diagnostic.primary is not None and not diagnostic.primary_active:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0139", "Die globale Hauptverantwortung ist keiner aktiven Person zugeordnet."
            ))
        if policy.require_active_deputy and diagnostic.deputy is not None and not diagnostic.deputy_active:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0140", "Die globale Sicherheitsstellvertretung ist keiner aktiven Person zugeordnet."
            ))
        if policy.require_distinct_users and diagnostic.same_user_assigned_twice:
            findings.append(GlobalSecurityStaffingFinding(
                "ERR-KICAD-0141", "Hauptverantwortung und Stellvertretung sind derselben Person zugeordnet."
            ))

        decision = (
            GlobalSecurityStaffingDecision.REJECTED
            if findings else GlobalSecurityStaffingDecision.APPROVED
        )
        return GlobalSecurityStaffingGateResult(decision, diagnostic, tuple(findings))
