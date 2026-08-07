"""Automatisierte Qualitätsgrenzen und Freigabeentscheidung für KiCad-Validierungen."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import sqlite3

from .identifiers import BusinessId
from .kicad_library_validation import KiCadValidationSeverity
from .kicad_validation_history import KiCadValidationHistoryRecord
from .kicad_validation_search import KiCadValidationSearchFilter, KiCadValidationSearchService


class KiCadReleaseDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True, slots=True)
class KiCadQualityPolicy:
    minimum_runs: int = 1
    require_latest_valid: bool = True
    maximum_latest_errors: int = 0
    maximum_latest_warnings: int | None = None
    maximum_latest_exceptions: int | None = None
    minimum_validity_rate: float | None = None
    forbidden_finding_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.minimum_runs < 1:
            raise ValueError("ERR-KICAD-0063: Die Mindestanzahl der Validierungsläufe muss mindestens 1 sein.")
        if self.maximum_latest_errors < 0:
            raise ValueError("ERR-KICAD-0064: Die maximale Fehlerzahl darf nicht negativ sein.")
        for value in (self.maximum_latest_warnings, self.maximum_latest_exceptions):
            if value is not None and value < 0:
                raise ValueError("ERR-KICAD-0065: Qualitätsgrenzen dürfen nicht negativ sein.")
        if self.minimum_validity_rate is not None and not 0.0 <= self.minimum_validity_rate <= 1.0:
            raise ValueError("ERR-KICAD-0066: Die Mindestgültigkeitsquote muss zwischen 0 und 1 liegen.")
        codes = tuple(dict.fromkeys(code.strip().upper() for code in self.forbidden_finding_codes if code.strip()))
        object.__setattr__(self, "forbidden_finding_codes", codes)


@dataclass(frozen=True, slots=True)
class KiCadQualityGateFinding:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class KiCadQualityGateResult:
    project_id: BusinessId
    decision: KiCadReleaseDecision
    evaluated_runs: int
    latest_validation: KiCadValidationHistoryRecord | None
    validity_rate: float
    latest_error_count: int
    latest_warning_count: int
    latest_exception_count: int
    findings: tuple[KiCadQualityGateFinding, ...]

    @property
    def approved(self) -> bool:
        return self.decision is KiCadReleaseDecision.APPROVED


class KiCadQualityGateService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._search = KiCadValidationSearchService(connection)

    def evaluate(
        self,
        *,
        project_id: BusinessId,
        policy: KiCadQualityPolicy | None = None,
    ) -> KiCadQualityGateResult:
        policy = policy or KiCadQualityPolicy()
        filters = KiCadValidationSearchFilter(project_id=project_id)
        trend = self._search.trend(filters)
        page = self._search.search(filters, page=1, page_size=1)
        latest = page.items[0] if page.items else None

        if trend.total_runs < policy.minimum_runs or latest is None:
            return KiCadQualityGateResult(
                project_id, KiCadReleaseDecision.INSUFFICIENT_DATA, trend.total_runs, latest,
                trend.validity_rate, 0, 0, 0,
                (KiCadQualityGateFinding(
                    "ERR-KICAD-0067",
                    f"Für die Freigabe werden mindestens {policy.minimum_runs} Validierungsläufe benötigt; vorhanden: {trend.total_runs}.",
                ),),
            )

        errors = sum(1 for item in latest.findings if item.severity is KiCadValidationSeverity.ERROR)
        warnings = sum(1 for item in latest.findings if item.severity is KiCadValidationSeverity.WARNING)
        findings: list[KiCadQualityGateFinding] = []

        if policy.require_latest_valid and not latest.valid:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0068", "Der jüngste KiCad-Validierungslauf ist ungültig."
            ))
        if errors > policy.maximum_latest_errors:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0069",
                f"Der jüngste Lauf enthält {errors} Fehler; zulässig sind höchstens {policy.maximum_latest_errors}.",
            ))
        if policy.maximum_latest_warnings is not None and warnings > policy.maximum_latest_warnings:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0070",
                f"Der jüngste Lauf enthält {warnings} Warnungen; zulässig sind höchstens {policy.maximum_latest_warnings}.",
            ))
        if policy.maximum_latest_exceptions is not None and latest.exception_count > policy.maximum_latest_exceptions:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0071",
                f"Der jüngste Lauf enthält {latest.exception_count} dokumentierte Ausnahmen; zulässig sind höchstens {policy.maximum_latest_exceptions}.",
            ))
        if policy.minimum_validity_rate is not None and trend.validity_rate < policy.minimum_validity_rate:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0072",
                f"Die Gültigkeitsquote beträgt {trend.validity_rate:.3f}; erforderlich sind mindestens {policy.minimum_validity_rate:.3f}.",
            ))

        latest_codes = {item.code.upper() for item in latest.findings}
        forbidden = sorted(latest_codes.intersection(policy.forbidden_finding_codes))
        if forbidden:
            findings.append(KiCadQualityGateFinding(
                "ERR-KICAD-0073",
                "Der jüngste Lauf enthält verbotene Finding-Codes: " + ", ".join(forbidden) + ".",
            ))

        decision = KiCadReleaseDecision.REJECTED if findings else KiCadReleaseDecision.APPROVED
        return KiCadQualityGateResult(
            project_id, decision, trend.total_runs, latest, trend.validity_rate,
            errors, warnings, latest.exception_count, tuple(findings),
        )
