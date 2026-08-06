"""Projektweite Command-Suche, Filterung und paginierte Diagnoseansicht."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .identifiers import BusinessId
from .project_command_lifecycle import CommandLifecycleService, CommandLifecycleState, CommandLifecycleView


@dataclass(frozen=True, slots=True)
class CommandSearchFilter:
    """Kombinierbare Filter für die projektweite Command-Diagnose."""

    project_id: BusinessId | None = None
    command_type: str | None = None
    state: CommandLifecycleState | None = None
    processed_from: datetime | None = None
    processed_until: datetime | None = None
    text: str | None = None

    def __post_init__(self) -> None:
        if self.processed_from is not None and self.processed_from.tzinfo is None:
            raise ValueError("processed_from benötigt einen Zeitzonenbezug.")
        if self.processed_until is not None and self.processed_until.tzinfo is None:
            raise ValueError("processed_until benötigt einen Zeitzonenbezug.")
        if self.processed_from is not None:
            object.__setattr__(self, "processed_from", self.processed_from.astimezone(timezone.utc))
        if self.processed_until is not None:
            object.__setattr__(self, "processed_until", self.processed_until.astimezone(timezone.utc))
        if (
            self.processed_from is not None
            and self.processed_until is not None
            and self.processed_from > self.processed_until
        ):
            raise ValueError("processed_from darf nicht nach processed_until liegen.")
        if self.command_type is not None:
            normalized = self.command_type.strip().lower()
            object.__setattr__(self, "command_type", normalized or None)
        if self.text is not None:
            normalized_text = self.text.strip().lower()
            object.__setattr__(self, "text", normalized_text or None)


@dataclass(frozen=True, slots=True)
class CommandSearchItem:
    command_id: BusinessId
    command_type: str
    project_id: BusinessId
    state: CommandLifecycleState
    last_processed_at: datetime
    correlation_id: str
    lifecycle: CommandLifecycleView


@dataclass(frozen=True, slots=True)
class CommandSearchPage:
    items: tuple[CommandSearchItem, ...]
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


class CommandSearchService:
    """Erzeugt eine stabile, seitenweise Diagnoseansicht über alle Commands."""

    def __init__(self, connection: sqlite3.Connection, lifecycle: CommandLifecycleService) -> None:
        self._connection = connection
        self._lifecycle = lifecycle

    def search(
        self,
        filters: CommandSearchFilter = CommandSearchFilter(),
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> CommandSearchPage:
        if page < 1:
            raise ValueError("Die Seitennummer muss mindestens 1 sein.")
        if not 1 <= page_size <= 200:
            raise ValueError("Die Seitengröße muss zwischen 1 und 200 liegen.")

        command_ids = self._command_ids()
        items = tuple(
            item
            for command_id in command_ids
            if (item := self._item(self._lifecycle.get(command_id))) is not None
            and self._matches(item, filters)
        )
        ordered = tuple(sorted(items, key=lambda item: (item.last_processed_at, str(item.command_id)), reverse=True))
        total_items = len(ordered)
        total_pages = (total_items + page_size - 1) // page_size if total_items else 0
        start = (page - 1) * page_size
        return CommandSearchPage(
            items=ordered[start : start + page_size],
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def _command_ids(self) -> tuple[BusinessId, ...]:
        rows = self._connection.execute(
            """
            SELECT command_id FROM projectos_command_executions
            UNION
            SELECT command_id FROM projectos_command_execution_archive
            ORDER BY command_id
            """
        ).fetchall()
        return tuple(BusinessId.parse(row["command_id"]) for row in rows)

    @staticmethod
    def _item(lifecycle: CommandLifecycleView) -> CommandSearchItem | None:
        records = (*lifecycle.archived_executions,)
        if lifecycle.current_execution is not None:
            records = (*records, lifecycle.current_execution)
        if not records:
            return None
        latest = max(records, key=lambda record: record.processed_at)
        original = lifecycle.original_execution or latest
        return CommandSearchItem(
            command_id=lifecycle.command_id,
            command_type=original.command_type,
            project_id=original.project_id,
            state=lifecycle.state,
            last_processed_at=latest.processed_at,
            correlation_id=latest.correlation_id,
            lifecycle=lifecycle,
        )

    @staticmethod
    def _matches(item: CommandSearchItem, filters: CommandSearchFilter) -> bool:
        if filters.project_id is not None and item.project_id != filters.project_id:
            return False
        if filters.command_type is not None and item.command_type != filters.command_type:
            return False
        if filters.state is not None and item.state is not filters.state:
            return False
        if filters.processed_from is not None and item.last_processed_at < filters.processed_from:
            return False
        if filters.processed_until is not None and item.last_processed_at > filters.processed_until:
            return False
        if filters.text is not None:
            haystack = " ".join(
                (
                    str(item.command_id).lower(),
                    item.command_type.lower(),
                    str(item.project_id).lower(),
                    item.correlation_id.lower(),
                )
            )
            if filters.text not in haystack:
                return False
        return True
