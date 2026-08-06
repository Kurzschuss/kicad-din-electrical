"""Suche und Sicherheitsdiagnose abgelehnter globaler Besetzungsfreigabeversuche."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_release_attempt_audit import GlobalSecurityStaffingReleaseAttemptRecord


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAttemptSearchFilter:
    actor_id: BusinessId | None = None
    acting_role: BusinessId | None = None
    permission_id: BusinessId | None = None
    denial_code: str | None = None
    correlation_id: CorrelationId | None = None
    reason_text: str | None = None
    from_timestamp: datetime | None = None
    until_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        for value in (self.from_timestamp, self.until_timestamp):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("ERR-KICAD-0154: Zeitfilter benötigen einen Zeitzonenbezug.")
        if self.from_timestamp and self.until_timestamp and self.from_timestamp > self.until_timestamp:
            raise ValueError("ERR-KICAD-0155: Der Beginn liegt nach dem Ende des Zeitraums.")


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseAttemptSearchPage:
    items: tuple[GlobalSecurityStaffingReleaseAttemptRecord, ...]
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
class GlobalSecurityStaffingReleaseAttemptSecurityDiagnostic:
    total_attempts: int
    distinct_actors: int
    attempts_without_actor: int
    distinct_roles: int
    first_attempt_at: datetime | None
    latest_attempt_at: datetime | None
    top_denial_codes: tuple[tuple[str, int], ...]
    top_permissions: tuple[tuple[str, int], ...]
    top_roles: tuple[tuple[str, int], ...]


class GlobalSecurityStaffingReleaseAttemptSearchService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def search(self, filters: GlobalSecurityStaffingReleaseAttemptSearchFilter | None = None, *, page: int = 1,
               page_size: int = 50) -> GlobalSecurityStaffingReleaseAttemptSearchPage:
        if page < 1:
            raise ValueError("ERR-KICAD-0156: Die Seitennummer muss mindestens 1 sein.")
        if page_size < 1 or page_size > 200:
            raise ValueError("ERR-KICAD-0157: Die Seitengröße muss zwischen 1 und 200 liegen.")
        filters = filters or GlobalSecurityStaffingReleaseAttemptSearchFilter()
        where, params = self._where(filters)
        total = int(self._connection.execute(
            f"SELECT COUNT(*) FROM projectos_global_security_staffing_release_attempt_audit {where}", params
        ).fetchone()[0])
        rows = self._connection.execute(
            f"SELECT * FROM projectos_global_security_staffing_release_attempt_audit {where} "
            "ORDER BY attempted_at DESC, attempt_id DESC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
        return GlobalSecurityStaffingReleaseAttemptSearchPage(
            tuple(_decode(row) for row in rows), page, page_size, total,
            math.ceil(total / page_size) if total else 0,
        )

    def diagnostic(self, filters: GlobalSecurityStaffingReleaseAttemptSearchFilter | None = None) -> GlobalSecurityStaffingReleaseAttemptSecurityDiagnostic:
        filters = filters or GlobalSecurityStaffingReleaseAttemptSearchFilter()
        where, params = self._where(filters)
        rows = self._connection.execute(
            f"SELECT * FROM projectos_global_security_staffing_release_attempt_audit {where} ORDER BY attempted_at",
            params,
        ).fetchall()
        records = tuple(_decode(row) for row in rows)
        actors = {r.actor_id for r in records if r.actor_id is not None}
        roles = {r.acting_role for r in records}
        codes = Counter(r.denial_code for r in records)
        permissions = Counter(str(r.permission_id) for r in records)
        role_counts = Counter(str(r.acting_role) for r in records)
        return GlobalSecurityStaffingReleaseAttemptSecurityDiagnostic(
            total_attempts=len(records),
            distinct_actors=len(actors),
            attempts_without_actor=sum(r.actor_id is None for r in records),
            distinct_roles=len(roles),
            first_attempt_at=records[0].attempted_at if records else None,
            latest_attempt_at=records[-1].attempted_at if records else None,
            top_denial_codes=tuple(codes.most_common(10)),
            top_permissions=tuple(permissions.most_common(10)),
            top_roles=tuple(role_counts.most_common(10)),
        )

    @staticmethod
    def _where(filters: GlobalSecurityStaffingReleaseAttemptSearchFilter) -> tuple[str, tuple[object, ...]]:
        clauses: list[str] = []
        params: list[object] = []
        for column, value in (("actor_id", filters.actor_id), ("acting_role", filters.acting_role),
                              ("permission_id", filters.permission_id), ("correlation_id", filters.correlation_id)):
            if value is not None:
                clauses.append(f"{column} = ?")
                params.append(str(value))
        if filters.denial_code:
            clauses.append("denial_code = ?")
            params.append(filters.denial_code.strip().upper())
        if filters.reason_text:
            clauses.append("LOWER(denial_reason) LIKE ?")
            params.append(f"%{filters.reason_text.strip().lower()}%")
        if filters.from_timestamp:
            clauses.append("attempted_at >= ?")
            params.append(filters.from_timestamp.astimezone(timezone.utc).isoformat())
        if filters.until_timestamp:
            clauses.append("attempted_at <= ?")
            params.append(filters.until_timestamp.astimezone(timezone.utc).isoformat())
        return ("WHERE " + " AND ".join(clauses) if clauses else "", tuple(params))


def _decode(row: tuple[object, ...]) -> GlobalSecurityStaffingReleaseAttemptRecord:
    return GlobalSecurityStaffingReleaseAttemptRecord(
        BusinessId(str(row[0])), datetime.fromisoformat(str(row[1])),
        BusinessId(str(row[2])) if row[2] else None, BusinessId(str(row[3])),
        BusinessId(str(row[4])), str(row[5]), str(row[6]), CorrelationId(str(row[7])),
    )
