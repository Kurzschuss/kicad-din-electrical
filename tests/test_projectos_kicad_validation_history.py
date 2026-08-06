from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    KiCadProjectValidationResult,
    KiCadValidationFinding,
    KiCadValidationSeverity,
    SQLiteKiCadValidationHistoryRepository,
)


def result(*findings: KiCadValidationFinding, target_count: int = 1) -> KiCadProjectValidationResult:
    return KiCadProjectValidationResult(None, tuple(findings), target_count)


def test_persists_and_reads_validation_history() -> None:
    repository = SQLiteKiCadValidationHistoryRepository(sqlite3.connect(":memory:"))
    finding = KiCadValidationFinding(
        "ERR-KICAD-0054", KiCadValidationSeverity.ERROR,
        "Erforderlicher Anschluss fehlt.", BusinessId("KICAD-SYM-0001"),
    )

    stored = repository.append(
        validation_id=BusinessId("KVAL-0001"),
        project_id=BusinessId("PRJ-0001"),
        recorded_at=datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc),
        correlation_id=CorrelationId("COR-00000001"),
        result=result(finding),
    )

    assert stored.valid is False
    assert stored.findings == (finding,)
    assert len(stored.fingerprint) == 64
    assert repository.get(BusinessId("KVAL-0001")) == stored


def test_history_is_sorted_newest_first() -> None:
    repository = SQLiteKiCadValidationHistoryRepository(sqlite3.connect(":memory:"))
    for sequence, hour in ((1, 10), (2, 11)):
        repository.append(
            validation_id=BusinessId(f"KVAL-000{sequence}"),
            project_id=BusinessId("PRJ-0001"),
            recorded_at=datetime(2026, 8, 6, hour, tzinfo=timezone.utc),
            correlation_id=CorrelationId(f"COR-{sequence:08d}"),
            result=result(),
        )

    assert [str(item.validation_id) for item in repository.list_for_project(BusinessId("PRJ-0001"))] == [
        "KVAL-0002", "KVAL-0001",
    ]


def test_compares_added_and_removed_findings() -> None:
    repository = SQLiteKiCadValidationHistoryRepository(sqlite3.connect(":memory:"))
    old_finding = KiCadValidationFinding("ERR-KICAD-0020", KiCadValidationSeverity.ERROR, "Symbol fehlt.")
    new_finding = KiCadValidationFinding("INFO-KICAD-0001", KiCadValidationSeverity.INFO, "Ausnahme dokumentiert.")
    repository.append(
        validation_id=BusinessId("KVAL-0001"), project_id=BusinessId("PRJ-0001"),
        recorded_at=datetime(2026, 8, 6, 10, tzinfo=timezone.utc),
        correlation_id=CorrelationId("COR-00000001"), result=result(old_finding),
    )
    repository.append(
        validation_id=BusinessId("KVAL-0002"), project_id=BusinessId("PRJ-0001"),
        recorded_at=datetime(2026, 8, 6, 11, tzinfo=timezone.utc),
        correlation_id=CorrelationId("COR-00000002"), result=result(new_finding),
    )

    comparison = repository.compare(BusinessId("KVAL-0001"), BusinessId("KVAL-0002"))

    assert comparison.added_findings == (new_finding,)
    assert comparison.removed_findings == (old_finding,)
    assert comparison.validity_changed is True
    assert comparison.exception_delta == 1


def test_rejects_duplicate_validation_id_and_naive_timestamp() -> None:
    repository = SQLiteKiCadValidationHistoryRepository(sqlite3.connect(":memory:"))
    arguments = dict(
        validation_id=BusinessId("KVAL-0001"), project_id=BusinessId("PRJ-0001"),
        recorded_at=datetime(2026, 8, 6, 10, tzinfo=timezone.utc),
        correlation_id=CorrelationId("COR-00000001"), result=result(),
    )
    repository.append(**arguments)
    with pytest.raises(ValueError, match="ERR-KICAD-0056"):
        repository.append(**arguments)
    with pytest.raises(ValueError, match="ERR-KICAD-0055"):
        repository.append(**{**arguments, "validation_id": BusinessId("KVAL-0002"), "recorded_at": datetime(2026, 8, 6, 10)})


def test_rejects_comparison_across_projects() -> None:
    repository = SQLiteKiCadValidationHistoryRepository(sqlite3.connect(":memory:"))
    for sequence, project in ((1, "PRJ-0001"), (2, "PRJ-0002")):
        repository.append(
            validation_id=BusinessId(f"KVAL-000{sequence}"), project_id=BusinessId(project),
            recorded_at=datetime(2026, 8, 6, 10 + sequence, tzinfo=timezone.utc),
            correlation_id=CorrelationId(f"COR-{sequence:08d}"), result=result(),
        )
    with pytest.raises(ValueError, match="ERR-KICAD-0058"):
        repository.compare(BusinessId("KVAL-0001"), BusinessId("KVAL-0002"))
