"""Suche, Filterung und Trenddiagnose persistierter KiCad-Validierungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import math
import sqlite3

from .identifiers import BusinessId
from .kicad_validation_history import KiCadValidationHistoryRecord, _decode_record


@dataclass(frozen=True, slots=True)
class KiCadValidationSearchFilter:
    project_id: BusinessId | None = None
    valid: bool | None = None
    has_exceptions: bool | None = None
    finding_code: str | None = None
    from_timestamp: datetime | None = None
    until_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        for value in (self.from_timestamp, self.until_timestamp):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("ERR-KICAD-0059: Zeitfilter benötigen einen Zeitzonenbezug.")
        if self.from_timestamp and self.until_timestamp and self.from_timestamp > self.until_timestamp:
            raise ValueError("ERR-KICAD-0060: Der Beginn des Suchzeitraums liegt nach dessen Ende.")
        code = self.finding_code.strip().upper() if self.finding_code else None
        object.__setattr__(self, "finding_code", code)


@dataclass(frozen=True, slots=True)
class KiCadValidationSearchPage:
    items: tuple[KiCadValidationHistoryRecord, ...]
    page: int
    page_size: int
    total_items: int
    total_pages: int

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


@dataclass(frozen=True, slots=True)
class KiCadValidationTrend:
    total_runs: int
    valid_runs: int
    invalid_runs: int
    validity_rate: float
    first_valid: bool | None
    latest_valid: bool | None
    validity_improved: bool
    first_error_count: int
    latest_error_count: int
    error_delta: int
    first_exception_count: int
    latest_exception_count: int
    exception_delta: int
    top_finding_codes: tuple[tuple[str, int], ...]


class KiCadValidationSearchService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def search(
        self,
        filters: KiCadValidationSearchFilter | None = None,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> KiCadValidationSearchPage:
        if page < 1:
            raise ValueError("ERR-KICAD-0061: Die Seitennummer muss mindestens 1 sein.")
        if page_size < 1 or page_size > 200:
            raise ValueError("ERR-KICAD-0062: Die Seitengröße muss zwischen 1 und 200 liegen.")
        filters = filters or KiCadValidationSearchFilter()
        where, params = self._where(filters)
        total = int(self._connection.execute(
            f"SELECT COUNT(*) FROM projectos_kicad_validation_history {where}", params
        ).fetchone()[0])
        rows = self._connection.execute(
            f"SELECT * FROM projectos_kicad_validation_history {where} "
            "ORDER BY recorded_at DESC, validation_id DESC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
        total_pages = math.ceil(total / page_size) if total else 0
        return KiCadValidationSearchPage(
            tuple(_decode_record(row) for row in rows), page, page_size, total, total_pages
        )

    def trend(self, filters: KiCadValidationSearchFilter | None = None) -> KiCadValidationTrend:
        filters = filters or KiCadValidationSearchFilter()
        where, params = self._where(filters)
        rows = self._connection.execute(
            f"SELECT * FROM projectos_kicad_validation_history {where} "
            "ORDER BY recorded_at ASC, validation_id ASC", params
        ).fetchall()
        records = tuple(_decode_record(row) for row in rows)
        if not records:
            return KiCadValidationTrend(0, 0, 0, 0.0, None, None, False, 0, 0, 0, 0, 0, 0, ())
        valid_runs = sum(1 for record in records if record.valid)
        error_counts = [sum(1 for item in record.findings if item.severity.value == "ERROR") for record in records]
        code_counts: dict[str, int] = {}
        for record in records:
            for item in record.findings:
                code_counts[item.code] = code_counts.get(item.code, 0) + 1
        top_codes = tuple(sorted(code_counts.items(), key=lambda item: (-item[1], item[0]))[:10])
        first, latest = records[0], records[-1]
        return KiCadValidationTrend(
            total_runs=len(records), valid_runs=valid_runs, invalid_runs=len(records) - valid_runs,
            validity_rate=valid_runs / len(records), first_valid=first.valid, latest_valid=latest.valid,
            validity_improved=(not first.valid and latest.valid),
            first_error_count=error_counts[0], latest_error_count=error_counts[-1],
            error_delta=error_counts[-1] - error_counts[0],
            first_exception_count=first.exception_count, latest_exception_count=latest.exception_count,
            exception_delta=latest.exception_count - first.exception_count,
            top_finding_codes=top_codes,
        )

    def _where(self, filters: KiCadValidationSearchFilter) -> tuple[str, tuple[object, ...]]:
        clauses: list[str] = []
        params: list[object] = []
        if filters.project_id is not None:
            clauses.append("project_id = ?")
            params.append(str(filters.project_id))
        if filters.valid is not None:
            clauses.append("valid = ?")
            params.append(int(filters.valid))
        if filters.has_exceptions is not None:
            clauses.append("exception_count > 0" if filters.has_exceptions else "exception_count = 0")
        if filters.finding_code:
            clauses.append("EXISTS (SELECT 1 FROM json_each(findings_json) WHERE json_extract(value, '$.code') = ?)")
            params.append(filters.finding_code)
        if filters.from_timestamp is not None:
            clauses.append("recorded_at >= ?")
            params.append(filters.from_timestamp.isoformat())
        if filters.until_timestamp is not None:
            clauses.append("recorded_at <= ?")
            params.append(filters.until_timestamp.isoformat())
        return ("WHERE " + " AND ".join(clauses) if clauses else "", tuple(params))
