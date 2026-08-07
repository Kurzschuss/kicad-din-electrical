"""Konfigurierbare Alarmbewertung abgelehnter KiCad-Freigabeversuche."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
import sqlite3

from .identifiers import BusinessId
from .kicad_release_attempt_search import (
    KiCadReleaseAttemptSearchFilter,
    KiCadReleaseAttemptSearchService,
)


class KiCadSecurityAlertLevel(StrEnum):
    CLEAR = "CLEAR"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class KiCadReleaseAttemptAlertPolicy:
    window: timedelta = timedelta(hours=24)
    warning_attempts: int = 3
    critical_attempts: int = 5
    warning_attempts_per_actor: int | None = 3
    critical_attempts_per_actor: int | None = 5
    warning_attempts_per_role: int | None = None
    critical_attempts_per_role: int | None = None
    critical_denial_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.window <= timedelta(0):
            raise ValueError("ERR-KICAD-0090: Das Alarmzeitfenster muss größer als null sein.")
        if self.warning_attempts < 1 or self.critical_attempts < 1:
            raise ValueError("ERR-KICAD-0091: Versuchsschwellen müssen mindestens 1 sein.")
        if self.critical_attempts < self.warning_attempts:
            raise ValueError("ERR-KICAD-0092: Die kritische Schwelle darf nicht unter der Warnschwelle liegen.")
        for warning, critical in (
            (self.warning_attempts_per_actor, self.critical_attempts_per_actor),
            (self.warning_attempts_per_role, self.critical_attempts_per_role),
        ):
            if warning is not None and warning < 1 or critical is not None and critical < 1:
                raise ValueError("ERR-KICAD-0093: Optionale Sicherheitsschwellen müssen mindestens 1 sein.")
            if warning is not None and critical is not None and critical < warning:
                raise ValueError("ERR-KICAD-0094: Eine kritische Sicherheitsschwelle darf nicht unter der Warnschwelle liegen.")
        codes = tuple(dict.fromkeys(code.strip().upper() for code in self.critical_denial_codes if code.strip()))
        object.__setattr__(self, "critical_denial_codes", codes)


@dataclass(frozen=True, slots=True)
class KiCadSecurityAlertFinding:
    code: str
    level: KiCadSecurityAlertLevel
    message: str
    subject_id: BusinessId | None = None


@dataclass(frozen=True, slots=True)
class KiCadReleaseAttemptAlertResult:
    project_id: BusinessId | None
    evaluated_at: datetime
    window_start: datetime
    total_attempts: int
    level: KiCadSecurityAlertLevel
    findings: tuple[KiCadSecurityAlertFinding, ...]

    @property
    def alert(self) -> bool:
        return self.level is not KiCadSecurityAlertLevel.CLEAR


class KiCadReleaseAttemptAlertService:
    """Bewertet beobachtete Ablehnungen, ohne Benutzer oder Projekte zu sperren."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._search = KiCadReleaseAttemptSearchService(connection)

    def evaluate(
        self,
        *,
        evaluated_at: datetime,
        project_id: BusinessId | None = None,
        policy: KiCadReleaseAttemptAlertPolicy | None = None,
    ) -> KiCadReleaseAttemptAlertResult:
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0095: Der Bewertungszeitpunkt benötigt eine Zeitzone.")
        policy = policy or KiCadReleaseAttemptAlertPolicy()
        window_start = evaluated_at - policy.window
        filters = KiCadReleaseAttemptSearchFilter(
            project_id=project_id,
            from_timestamp=window_start,
            until_timestamp=evaluated_at,
        )
        diagnostic = self._search.diagnostic(filters)
        findings: list[KiCadSecurityAlertFinding] = []

        self._append_threshold(
            findings, diagnostic.total_attempts,
            policy.warning_attempts, policy.critical_attempts,
            "WARN-KICAD-0002", "ERR-KICAD-0096",
            "abgelehnte Freigabeversuche im Zeitfenster",
        )

        for actor_id, count in diagnostic.top_actors:
            self._append_subject_threshold(
                findings, count,
                policy.warning_attempts_per_actor, policy.critical_attempts_per_actor,
                "WARN-KICAD-0003", "ERR-KICAD-0097",
                "abgelehnte Versuche durch Benutzer", actor_id,
            )
        for role_id, count in diagnostic.top_roles:
            self._append_subject_threshold(
                findings, count,
                policy.warning_attempts_per_role, policy.critical_attempts_per_role,
                "WARN-KICAD-0004", "ERR-KICAD-0098",
                "abgelehnte Versuche mit Rolle", role_id,
            )

        observed_codes = {code for code, _ in diagnostic.top_denial_codes}
        for code in sorted(observed_codes.intersection(policy.critical_denial_codes)):
            findings.append(KiCadSecurityAlertFinding(
                "ERR-KICAD-0099", KiCadSecurityAlertLevel.CRITICAL,
                f"Kritischer Ablehnungscode wurde beobachtet: {code}.",
            ))

        level = KiCadSecurityAlertLevel.CLEAR
        if any(item.level is KiCadSecurityAlertLevel.CRITICAL for item in findings):
            level = KiCadSecurityAlertLevel.CRITICAL
        elif findings:
            level = KiCadSecurityAlertLevel.WARNING
        ordered = tuple(sorted(findings, key=lambda item: (item.level.value, item.code, str(item.subject_id or ""), item.message)))
        return KiCadReleaseAttemptAlertResult(
            project_id, evaluated_at, window_start, diagnostic.total_attempts, level, ordered
        )

    @staticmethod
    def _append_threshold(findings, count, warning, critical, warning_code, critical_code, label) -> None:
        if count >= critical:
            findings.append(KiCadSecurityAlertFinding(
                critical_code, KiCadSecurityAlertLevel.CRITICAL,
                f"{count} {label}; kritische Schwelle: {critical}.",
            ))
        elif count >= warning:
            findings.append(KiCadSecurityAlertFinding(
                warning_code, KiCadSecurityAlertLevel.WARNING,
                f"{count} {label}; Warnschwelle: {warning}.",
            ))

    @staticmethod
    def _append_subject_threshold(findings, count, warning, critical, warning_code, critical_code, label, subject_id) -> None:
        if critical is not None and count >= critical:
            findings.append(KiCadSecurityAlertFinding(
                critical_code, KiCadSecurityAlertLevel.CRITICAL,
                f"{count} {label} {subject_id}; kritische Schwelle: {critical}.", subject_id,
            ))
        elif warning is not None and count >= warning:
            findings.append(KiCadSecurityAlertFinding(
                warning_code, KiCadSecurityAlertLevel.WARNING,
                f"{count} {label} {subject_id}; Warnschwelle: {warning}.", subject_id,
            ))
