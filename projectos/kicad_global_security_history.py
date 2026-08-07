"""Historie, Suche und Zustandsdiagnose globaler Sicherheitsverantwortungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import sqlite3

from .identifiers import BusinessId
from .identity_persistence import SQLiteIdentityRepository
from .kicad_global_security import (
    GlobalSecurityResponsibility,
    GlobalSecurityResponsibilityType,
    SQLiteGlobalSecurityResponsibilityRepository,
)


@dataclass(frozen=True, slots=True)
class GlobalSecurityResponsibilityHistoryRecord:
    change_id: BusinessId
    responsibility: GlobalSecurityResponsibilityType
    user_id: BusinessId
    assigned_at: datetime
    reason: str
    previous_user_id: BusinessId | None


@dataclass(frozen=True, slots=True)
class GlobalSecurityResponsibilitySearchFilter:
    responsibility: GlobalSecurityResponsibilityType | None = None
    user_id: BusinessId | None = None
    from_timestamp: datetime | None = None
    until_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        for value in (self.from_timestamp, self.until_timestamp):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("ERR-KICAD-0129: Zeitfilter benötigen einen Zeitzonenbezug.")
        if self.from_timestamp and self.until_timestamp and self.from_timestamp > self.until_timestamp:
            raise ValueError("ERR-KICAD-0130: Der Beginn liegt nach dem Ende des Zeitraums.")


@dataclass(frozen=True, slots=True)
class GlobalSecurityResponsibilitySearchPage:
    items: tuple[GlobalSecurityResponsibilityHistoryRecord, ...]
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
class GlobalSecurityResponsibilityDiagnostic:
    primary: GlobalSecurityResponsibility | None
    deputy: GlobalSecurityResponsibility | None
    primary_active: bool
    deputy_active: bool
    complete: bool
    same_user_assigned_twice: bool
    total_changes: int
    latest_change_at: datetime | None


class SQLiteTrackedGlobalSecurityResponsibilityRepository(SQLiteGlobalSecurityResponsibilityRepository):
    """Erweitert die operative Zuordnung um eine nur anhängbare Wechselhistorie."""

    def __init__(self, connection: sqlite3.Connection, identities: SQLiteIdentityRepository) -> None:
        super().__init__(connection, identities)
        self._connection = connection
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projectos_global_security_responsibility_history (
                change_id TEXT PRIMARY KEY,
                responsibility TEXT NOT NULL,
                user_id TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                reason TEXT NOT NULL,
                previous_user_id TEXT
            )"""
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_global_security_history_time "
            "ON projectos_global_security_responsibility_history(assigned_at DESC, change_id DESC)"
        )
        self._connection.commit()

    def assign_tracked(
        self,
        value: GlobalSecurityResponsibility,
        *,
        change_id: BusinessId,
    ) -> GlobalSecurityResponsibilityHistoryRecord:
        previous = self.get(value.responsibility)
        try:
            self._connection.execute("BEGIN")
            super().assign(value)
            self._connection.execute(
                "INSERT INTO projectos_global_security_responsibility_history VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(change_id), value.responsibility.value, str(value.user_id),
                    value.assigned_at.isoformat(), value.reason,
                    str(previous.user_id) if previous else None,
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            self._connection.rollback()
            raise ValueError("ERR-KICAD-0131: Die Verantwortungswechselkennung ist bereits vorhanden.") from exc
        return self.get_change(change_id)

    def get_change(self, change_id: BusinessId) -> GlobalSecurityResponsibilityHistoryRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_global_security_responsibility_history WHERE change_id = ?",
            (str(change_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0132: Verantwortungswechsel wurde nicht gefunden.")
        return _decode(row)


class GlobalSecurityResponsibilityHistoryService:
    def __init__(self, connection: sqlite3.Connection, identities: SQLiteIdentityRepository) -> None:
        self._connection = connection
        self._identities = identities
        self._current = SQLiteGlobalSecurityResponsibilityRepository(connection, identities)

    def search(
        self,
        filters: GlobalSecurityResponsibilitySearchFilter | None = None,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> GlobalSecurityResponsibilitySearchPage:
        if page < 1:
            raise ValueError("ERR-KICAD-0133: Die Seitennummer muss mindestens 1 sein.")
        if page_size < 1 or page_size > 200:
            raise ValueError("ERR-KICAD-0134: Die Seitengröße muss zwischen 1 und 200 liegen.")
        filters = filters or GlobalSecurityResponsibilitySearchFilter()
        clauses: list[str] = []
        params: list[object] = []
        if filters.responsibility:
            clauses.append("responsibility = ?")
            params.append(filters.responsibility.value)
        if filters.user_id:
            clauses.append("user_id = ?")
            params.append(str(filters.user_id))
        if filters.from_timestamp:
            clauses.append("assigned_at >= ?")
            params.append(filters.from_timestamp.astimezone(timezone.utc).isoformat())
        if filters.until_timestamp:
            clauses.append("assigned_at <= ?")
            params.append(filters.until_timestamp.astimezone(timezone.utc).isoformat())
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        total = int(self._connection.execute(
            f"SELECT COUNT(*) FROM projectos_global_security_responsibility_history {where}", tuple(params)
        ).fetchone()[0])
        rows = self._connection.execute(
            f"SELECT * FROM projectos_global_security_responsibility_history {where} "
            "ORDER BY assigned_at DESC, change_id DESC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
        return GlobalSecurityResponsibilitySearchPage(
            tuple(_decode(row) for row in rows), page, page_size, total,
            math.ceil(total / page_size) if total else 0,
        )

    def diagnostic(self) -> GlobalSecurityResponsibilityDiagnostic:
        primary = self._current.get(GlobalSecurityResponsibilityType.PRIMARY)
        deputy = self._current.get(GlobalSecurityResponsibilityType.DEPUTY)
        primary_user = self._identities.get_user(primary.user_id) if primary else None
        deputy_user = self._identities.get_user(deputy.user_id) if deputy else None
        row = self._connection.execute(
            "SELECT COUNT(*), MAX(assigned_at) FROM projectos_global_security_responsibility_history"
        ).fetchone()
        same = primary is not None and deputy is not None and primary.user_id == deputy.user_id
        primary_active = bool(primary_user and primary_user.active)
        deputy_active = bool(deputy_user and deputy_user.active)
        return GlobalSecurityResponsibilityDiagnostic(
            primary, deputy, primary_active, deputy_active,
            bool(primary and deputy and primary_active and deputy_active and not same),
            same, int(row[0]), datetime.fromisoformat(str(row[1])) if row[1] else None,
        )


def _decode(row: tuple[object, ...]) -> GlobalSecurityResponsibilityHistoryRecord:
    return GlobalSecurityResponsibilityHistoryRecord(
        BusinessId(str(row[0])), GlobalSecurityResponsibilityType(str(row[1])),
        BusinessId(str(row[2])), datetime.fromisoformat(str(row[3])), str(row[4]),
        BusinessId(str(row[5])) if row[5] else None,
    )
