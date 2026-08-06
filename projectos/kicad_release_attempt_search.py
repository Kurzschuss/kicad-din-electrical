"""Suche, Filterung und Sicherheitsdiagnose abgelehnter KiCad-Freigabeversuche."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
import sqlite3

from .identifiers import BusinessId
from .kicad_release_attempt_audit import KiCadReleaseAttemptAuditRecord, _decode_record


@dataclass(frozen=True, slots=True)
class KiCadReleaseAttemptSearchFilter:
    project_id: BusinessId | None = None
    actor_id: BusinessId | None = None
    acting_role: BusinessId | None = None
    permission_id: BusinessId | None = None
    denial_code: str | None = None
    from_timestamp: datetime | None = None
    until_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        for value in (self.from_timestamp, self.until_timestamp):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("ERR-KICAD-0086: Zeitfilter benötigen einen Zeitzonenbezug.")
        if self.from_timestamp and self.until_timestamp and self.from_timestamp > self.until_timestamp:
            raise ValueError("ERR-KICAD-0087: Der Beginn des Suchzeitraums liegt nach dessen Ende.")
        code = self.denial_code.strip().upper() if self.denial_code else None
        object.__setattr__(self, "denial_code", code)


@dataclass(frozen=True, slots=True)
class KiCadReleaseAttemptSearchPage:
    items: tuple[KiCadReleaseAttemptAuditRecord, ...]
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
class KiCadReleaseAttemptSecurityDiagnostic:
    total_attempts: int
    unique_projects: int
    unique_actors: int
    unique_roles: int
    top_denial_codes: tuple[tuple[str, int], ...]
    top_actors: tuple[tuple[BusinessId, int], ...]
    top_roles: tuple[tuple[BusinessId, int], ...]
    first_attempt_at: datetime | None
    latest_attempt_at: datetime | None


class KiCadReleaseAttemptSearchService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def search(
        self,
        filters: KiCadReleaseAttemptSearchFilter | None = None,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> KiCadReleaseAttemptSearchPage:
        if page < 1:
            raise ValueError("ERR-KICAD-0088: Die Seitennummer muss mindestens 1 sein.")
        if page_size < 1 or page_size > 200:
            raise ValueError("ERR-KICAD-0089: Die Seitengröße muss zwischen 1 und 200 liegen.")
        filters = filters or KiCadReleaseAttemptSearchFilter()
        where, params = self._where(filters)
        total = int(self._connection.execute(
            f"SELECT COUNT(*) FROM projectos_kicad_release_attempt_audit {where}", params
        ).fetchone()[0])
        rows = self._connection.execute(
            f"SELECT * FROM projectos_kicad_release_attempt_audit {where} "
            "ORDER BY attempted_at DESC, attempt_id DESC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
        return KiCadReleaseAttemptSearchPage(
            tuple(_decode_record(row) for row in rows), page, page_size, total,
            math.ceil(total / page_size) if total else 0,
        )

    def diagnostic(
        self,
        filters: KiCadReleaseAttemptSearchFilter | None = None,
    ) -> KiCadReleaseAttemptSecurityDiagnostic:
        filters = filters or KiCadReleaseAttemptSearchFilter()
        where, params = self._where(filters)
        rows = self._connection.execute(
            f"SELECT * FROM projectos_kicad_release_attempt_audit {where} "
            "ORDER BY attempted_at ASC, attempt_id ASC", params
        ).fetchall()
        records = tuple(_decode_record(row) for row in rows)
        if not records:
            return KiCadReleaseAttemptSecurityDiagnostic(0, 0, 0, 0, (), (), (), None, None)
        codes: dict[str, int] = {}
        actors: dict[BusinessId, int] = {}
        roles: dict[BusinessId, int] = {}
        for record in records:
            codes[record.denial_code] = codes.get(record.denial_code, 0) + 1
            actors[record.actor_id] = actors.get(record.actor_id, 0) + 1
            roles[record.acting_role] = roles.get(record.acting_role, 0) + 1
        top_codes = tuple(sorted(codes.items(), key=lambda item: (-item[1], item[0]))[:10])
        top_actors = tuple(sorted(actors.items(), key=lambda item: (-item[1], str(item[0])))[:10])
        top_roles = tuple(sorted(roles.items(), key=lambda item: (-item[1], str(item[0])))[:10])
        return KiCadReleaseAttemptSecurityDiagnostic(
            total_attempts=len(records),
            unique_projects=len({record.project_id for record in records}),
            unique_actors=len(actors),
            unique_roles=len(roles),
            top_denial_codes=top_codes,
            top_actors=top_actors,
            top_roles=top_roles,
            first_attempt_at=records[0].attempted_at,
            latest_attempt_at=records[-1].attempted_at,
        )

    @staticmethod
    def _where(filters: KiCadReleaseAttemptSearchFilter) -> tuple[str, tuple[object, ...]]:
        clauses: list[str] = []
        params: list[object] = []
        for column, value in (
            ("project_id", filters.project_id),
            ("actor_id", filters.actor_id),
            ("acting_role", filters.acting_role),
            ("permission_id", filters.permission_id),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                params.append(str(value))
        if filters.denial_code:
            clauses.append("denial_code = ?")
            params.append(filters.denial_code)
        if filters.from_timestamp is not None:
            clauses.append("attempted_at >= ?")
            params.append(filters.from_timestamp.isoformat())
        if filters.until_timestamp is not None:
            clauses.append("attempted_at <= ?")
            params.append(filters.until_timestamp.isoformat())
        return ("WHERE " + " AND ".join(clauses) if clauses else "", tuple(params))
