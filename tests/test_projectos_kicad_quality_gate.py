from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    KiCadProjectValidationResult,
    KiCadQualityGateService,
    KiCadQualityPolicy,
    KiCadReleaseDecision,
    KiCadValidationFinding,
    KiCadValidationSeverity,
    SQLiteKiCadValidationHistoryRepository,
)


PROJECT = BusinessId("PRJ-KICAD")


def result(*findings: KiCadValidationFinding, target_count: int = 1) -> KiCadProjectValidationResult:
    return KiCadProjectValidationResult(None, tuple(findings), target_count)


def append(
    repository: SQLiteKiCadValidationHistoryRepository,
    sequence: int,
    validation_result: KiCadProjectValidationResult,
) -> None:
    repository.append(
        validation_id=BusinessId(f"KVAL-{sequence:04d}"),
        project_id=PROJECT,
        recorded_at=datetime(2026, 8, sequence, 12, 0, tzinfo=timezone.utc),
        correlation_id=CorrelationId.from_sequence(sequence),
        result=validation_result,
    )


def test_approves_valid_latest_run_with_default_policy() -> None:
    connection = sqlite3.connect(":memory:")
    repository = SQLiteKiCadValidationHistoryRepository(connection)
    append(repository, 1, result())

    gate = KiCadQualityGateService(connection).evaluate(project_id=PROJECT)

    assert gate.decision is KiCadReleaseDecision.APPROVED
    assert gate.approved
    assert gate.latest_error_count == 0


def test_reports_insufficient_data() -> None:
    connection = sqlite3.connect(":memory:")
    SQLiteKiCadValidationHistoryRepository(connection)

    gate = KiCadQualityGateService(connection).evaluate(
        project_id=PROJECT,
        policy=KiCadQualityPolicy(minimum_runs=2),
    )

    assert gate.decision is KiCadReleaseDecision.INSUFFICIENT_DATA
    assert gate.findings[0].code == "ERR-KICAD-0067"


def test_rejects_invalid_latest_run_and_error_limit() -> None:
    connection = sqlite3.connect(":memory:")
    repository = SQLiteKiCadValidationHistoryRepository(connection)
    append(repository, 1, result(KiCadValidationFinding(
        "ERR-KICAD-9999", KiCadValidationSeverity.ERROR, "Fehler"
    )))

    gate = KiCadQualityGateService(connection).evaluate(project_id=PROJECT)

    assert gate.decision is KiCadReleaseDecision.REJECTED
    assert {item.code for item in gate.findings} == {"ERR-KICAD-0068", "ERR-KICAD-0069"}


def test_applies_warning_exception_rate_and_forbidden_code_limits() -> None:
    connection = sqlite3.connect(":memory:")
    repository = SQLiteKiCadValidationHistoryRepository(connection)
    append(repository, 1, result(KiCadValidationFinding(
        "ERR-KICAD-OLD", KiCadValidationSeverity.ERROR, "Alt"
    )))
    append(repository, 2, result(
        KiCadValidationFinding("WARN-KICAD-0001", KiCadValidationSeverity.WARNING, "Warnung"),
        KiCadValidationFinding("INFO-KICAD-0001", KiCadValidationSeverity.INFO, "Ausnahme"),
    ))

    gate = KiCadQualityGateService(connection).evaluate(
        project_id=PROJECT,
        policy=KiCadQualityPolicy(
            maximum_latest_warnings=0,
            maximum_latest_exceptions=0,
            minimum_validity_rate=0.75,
            forbidden_finding_codes=("warn-kicad-0001",),
        ),
    )

    assert gate.decision is KiCadReleaseDecision.REJECTED
    assert {item.code for item in gate.findings} == {
        "ERR-KICAD-0070", "ERR-KICAD-0071", "ERR-KICAD-0072", "ERR-KICAD-0073"
    }


def test_rejects_invalid_policy_values() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0063"):
        KiCadQualityPolicy(minimum_runs=0)
    with pytest.raises(ValueError, match="ERR-KICAD-0064"):
        KiCadQualityPolicy(maximum_latest_errors=-1)
    with pytest.raises(ValueError, match="ERR-KICAD-0065"):
        KiCadQualityPolicy(maximum_latest_exceptions=-1)
    with pytest.raises(ValueError, match="ERR-KICAD-0066"):
        KiCadQualityPolicy(minimum_validity_rate=1.1)
