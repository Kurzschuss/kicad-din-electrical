from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

import pytest

from projectos import (
    BusinessId, CorrelationId, KiCadProjectValidationResult,
    KiCadValidationFinding, KiCadValidationSearchFilter,
    KiCadValidationSearchService, KiCadValidationSeverity,
    SQLiteKiCadValidationHistoryRepository,
)


def _result(*, valid: bool, code: str | None = None, exceptions: int = 0) -> KiCadProjectValidationResult:
    findings = () if code is None else (
        KiCadValidationFinding(code, KiCadValidationSeverity.ERROR, code),
    )
    if exceptions:
        findings += tuple(
            KiCadValidationFinding("INFO-KICAD-0001", KiCadValidationSeverity.INFO, f"Ausnahme {i}")
            for i in range(exceptions)
        )
    return KiCadProjectValidationResult(None, findings, 1)


def _service() -> KiCadValidationSearchService:
    connection = sqlite3.connect(":memory:")
    repository = SQLiteKiCadValidationHistoryRepository(connection)
    data = (
        ("VAL-0001", "PRJ-A", "2026-08-01T10:00:00+00:00", False, "ERR-KICAD-0054", 0),
        ("VAL-0002", "PRJ-A", "2026-08-02T10:00:00+00:00", False, "ERR-KICAD-0022", 1),
        ("VAL-0003", "PRJ-A", "2026-08-03T10:00:00+00:00", True, None, 0),
        ("VAL-0004", "PRJ-B", "2026-08-04T10:00:00+00:00", True, None, 0),
    )
    for index, (validation_id, project_id, timestamp, valid, code, exceptions) in enumerate(data, 1):
        repository.append(
            validation_id=BusinessId(validation_id), project_id=BusinessId(project_id),
            recorded_at=datetime.fromisoformat(timestamp), correlation_id=CorrelationId.from_sequence(index),
            result=_result(valid=valid, code=code, exceptions=exceptions),
        )
    return KiCadValidationSearchService(connection)


def test_combined_filters_and_stable_order() -> None:
    page = _service().search(KiCadValidationSearchFilter(project_id=BusinessId("PRJ-A"), valid=False))
    assert [str(item.validation_id) for item in page.items] == ["VAL-0002", "VAL-0001"]


def test_finding_code_and_exception_filter() -> None:
    page = _service().search(KiCadValidationSearchFilter(
        finding_code="err-kicad-0022", has_exceptions=True,
    ))
    assert [str(item.validation_id) for item in page.items] == ["VAL-0002"]


def test_pagination() -> None:
    page = _service().search(page=2, page_size=2)
    assert page.total_items == 4
    assert page.total_pages == 2
    assert page.has_previous is True
    assert page.has_next is False


def test_trend_detects_improvement() -> None:
    trend = _service().trend(KiCadValidationSearchFilter(project_id=BusinessId("PRJ-A")))
    assert trend.total_runs == 3
    assert trend.valid_runs == 1
    assert trend.validity_improved is True
    assert trend.error_delta == -1
    assert trend.top_finding_codes[0][1] >= 1


def test_empty_trend_is_defined() -> None:
    trend = _service().trend(KiCadValidationSearchFilter(project_id=BusinessId("PRJ-X")))
    assert trend.total_runs == 0
    assert trend.first_valid is None


def test_rejects_invalid_time_and_pagination() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0059"):
        KiCadValidationSearchFilter(from_timestamp=datetime(2026, 8, 1))
    with pytest.raises(ValueError, match="ERR-KICAD-0060"):
        KiCadValidationSearchFilter(
            from_timestamp=datetime(2026, 8, 2, tzinfo=timezone.utc),
            until_timestamp=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )
    with pytest.raises(ValueError, match="ERR-KICAD-0061"):
        _service().search(page=0)
    with pytest.raises(ValueError, match="ERR-KICAD-0062"):
        _service().search(page_size=201)
