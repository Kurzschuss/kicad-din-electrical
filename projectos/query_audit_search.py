"""Query-Zugriffsdiagnose, Filterung und projektbezogene Audit-Auswertung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from collections import Counter

from .audit import AuditEntry
from .identifiers import BusinessId, CorrelationId
from .sqlite_audit import SQLiteAuditRepository

_QUERY_ACTIONS = frozenset({"project_query_accessed", "project_query_denied"})


@dataclass(frozen=True, slots=True)
class QueryAuditFilter:
    project_id: BusinessId | None = None
    actor_id: BusinessId | None = None
    acting_role: BusinessId | None = None
    permission_id: BusinessId | None = None
    query_type: str | None = None
    allowed: bool | None = None
    occurred_from: datetime | None = None
    occurred_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.occurred_from is not None:
            if self.occurred_from.tzinfo is None:
                raise ValueError("ERR-PRJ-QRY-0008: occurred_from benötigt einen Zeitzonenbezug.")
            object.__setattr__(self, "occurred_from", self.occurred_from.astimezone(timezone.utc))
        if self.occurred_until is not None:
            if self.occurred_until.tzinfo is None:
                raise ValueError("ERR-PRJ-QRY-0008: occurred_until benötigt einen Zeitzonenbezug.")
            object.__setattr__(self, "occurred_until", self.occurred_until.astimezone(timezone.utc))
        if (
            self.occurred_from is not None
            and self.occurred_until is not None
            and self.occurred_from > self.occurred_until
        ):
            raise ValueError("ERR-PRJ-QRY-0008: occurred_from darf nicht nach occurred_until liegen.")
        if self.query_type is not None:
            normalized = self.query_type.strip().lower()
            object.__setattr__(self, "query_type", normalized or None)


@dataclass(frozen=True, slots=True)
class QueryAuditItem:
    audit_id: BusinessId
    occurred_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    permission_id: BusinessId
    project_id: BusinessId | None
    query_id: BusinessId
    query_type: str
    allowed: bool
    correlation_id: CorrelationId
    message_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QueryAuditPage:
    items: tuple[QueryAuditItem, ...]
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
class QueryAuditStatistics:
    total: int
    allowed: int
    denied: int
    denial_rate: float
    by_query_type: tuple[tuple[str, int], ...]
    by_actor: tuple[tuple[BusinessId, int], ...]
    by_role: tuple[tuple[BusinessId, int], ...]
    by_permission: tuple[tuple[BusinessId, int], ...]


class QueryAuditSearchService:
    """Liest ausschließlich sicherheitsrelevante Query-Audit-Einträge aus."""

    def __init__(self, audit: SQLiteAuditRepository) -> None:
        self._audit = audit

    def search(
        self,
        filters: QueryAuditFilter = QueryAuditFilter(),
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> QueryAuditPage:
        if page < 1:
            raise ValueError("ERR-PRJ-QRY-0010: Die Seitennummer muss mindestens 1 sein.")
        if not 1 <= page_size <= 200:
            raise ValueError("ERR-PRJ-QRY-0009: Die Seitengröße muss zwischen 1 und 200 liegen.")
        items = tuple(item for item in self._items() if self._matches(item, filters))
        ordered = tuple(sorted(items, key=lambda item: (item.occurred_at, str(item.audit_id)), reverse=True))
        total_items = len(ordered)
        total_pages = (total_items + page_size - 1) // page_size if total_items else 0
        start = (page - 1) * page_size
        return QueryAuditPage(
            items=ordered[start : start + page_size],
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def count(self, filters: QueryAuditFilter = QueryAuditFilter()) -> int:
        return sum(1 for item in self._items() if self._matches(item, filters))

    def statistics(self, filters: QueryAuditFilter = QueryAuditFilter()) -> QueryAuditStatistics:
        items = tuple(item for item in self._items() if self._matches(item, filters))
        allowed = sum(item.allowed for item in items)
        denied = len(items) - allowed
        return QueryAuditStatistics(
            total=len(items),
            allowed=allowed,
            denied=denied,
            denial_rate=(denied / len(items)) if items else 0.0,
            by_query_type=self._rank(item.query_type for item in items),
            by_actor=self._rank(item.actor_id for item in items),
            by_role=self._rank(item.acting_role for item in items),
            by_permission=self._rank(item.permission_id for item in items),
        )

    def _items(self) -> tuple[QueryAuditItem, ...]:
        return tuple(
            item
            for entry in self._audit.all()
            if entry.action in _QUERY_ACTIONS
            if (item := self._decode(entry)) is not None
        )

    @staticmethod
    def _decode(entry: AuditEntry) -> QueryAuditItem | None:
        values = entry.new_values
        query_id = values.get("query_id")
        query_type = values.get("query_type")
        allowed = values.get("allowed")
        if not isinstance(query_id, str) or not isinstance(query_type, str) or not isinstance(allowed, bool):
            return None
        project_value = values.get("project_id")
        project_id = BusinessId.parse(project_value) if isinstance(project_value, str) and project_value else None
        raw_codes = values.get("message_codes", ())
        message_codes = tuple(str(code) for code in raw_codes) if isinstance(raw_codes, (list, tuple)) else ()
        return QueryAuditItem(
            audit_id=entry.audit_id,
            occurred_at=entry.occurred_at,
            actor_id=entry.actor_id,
            acting_role=entry.acting_role,
            permission_id=entry.permission_id,
            project_id=project_id,
            query_id=BusinessId.parse(query_id),
            query_type=query_type,
            allowed=allowed,
            correlation_id=entry.correlation_id,
            message_codes=message_codes,
        )

    @staticmethod
    def _matches(item: QueryAuditItem, filters: QueryAuditFilter) -> bool:
        if filters.project_id is not None and item.project_id != filters.project_id:
            return False
        if filters.actor_id is not None and item.actor_id != filters.actor_id:
            return False
        if filters.acting_role is not None and item.acting_role != filters.acting_role:
            return False
        if filters.permission_id is not None and item.permission_id != filters.permission_id:
            return False
        if filters.query_type is not None and item.query_type != filters.query_type:
            return False
        if filters.allowed is not None and item.allowed is not filters.allowed:
            return False
        if filters.occurred_from is not None and item.occurred_at < filters.occurred_from:
            return False
        if filters.occurred_until is not None and item.occurred_at > filters.occurred_until:
            return False
        return True

    @staticmethod
    def _rank(values) -> tuple[tuple[object, int], ...]:
        counts = Counter(values)
        return tuple(sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))[:10])
