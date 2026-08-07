"""Standardisierte Query-Pipeline für Command-Lebenszyklus, Suche und Diagnose."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Mapping

from .application import Query
from .identifiers import BusinessId
from .project_command_admin import CommandAdministrationService, CommandExecutionDiagnostic
from .project_command_lifecycle import CommandLifecycleService, CommandLifecycleState, CommandLifecycleView
from .project_command_search import CommandSearchFilter, CommandSearchPage, CommandSearchService
from .results import MessageSeverity, Result, ResultMessage

QUERY_COMMAND_LIFECYCLE = "project.command.lifecycle"
QUERY_COMMAND_SEARCH = "project.command.search"
QUERY_COMMAND_DIAGNOSTIC = "project.command.diagnostic"


@dataclass(frozen=True, slots=True)
class ProjectQueryExecutionResult:
    """Einheitlicher Ergebnisvertrag einer ProjectOS-Query."""

    query: Query
    value: object


ProjectQueryHandler = Callable[[Query], object]


class ProjectQueryPipeline:
    """Registriert und verarbeitet zustandsfreie ProjectOS-Queries deterministisch."""

    def __init__(self) -> None:
        self._handlers: dict[str, ProjectQueryHandler] = {}

    def register(self, query_type: str, handler: ProjectQueryHandler) -> None:
        normalized = Query(
            query_id=BusinessId("QRY-TYPE-CHECK"),
            query_type=query_type,
            correlation_id=self._dummy_correlation_id(),
        ).query_type
        if normalized in self._handlers:
            raise ValueError(f"Für {normalized} ist bereits ein Query-Handler registriert.")
        self._handlers[normalized] = handler

    def execute(self, query: Query) -> Result[ProjectQueryExecutionResult]:
        handler = self._handlers.get(query.query_type)
        if handler is None:
            return Result.failure(
                ResultMessage(
                    BusinessId("ERR-PRJ-QRY-0001"),
                    MessageSeverity.ERROR,
                    f"Kein ProjectOS-Query-Handler für {query.query_type} registriert.",
                ),
                correlation_id=query.correlation_id,
            )
        try:
            value = handler(query)
        except (KeyError, TypeError, ValueError) as exc:
            return Result.failure(
                ResultMessage(
                    BusinessId("ERR-PRJ-QRY-0002"),
                    MessageSeverity.ERROR,
                    str(exc),
                    parameters={"query_type": query.query_type},
                ),
                correlation_id=query.correlation_id,
            )
        return Result.success(
            ProjectQueryExecutionResult(query=query, value=value),
            correlation_id=query.correlation_id,
        )

    @staticmethod
    def _dummy_correlation_id():
        from .identifiers import CorrelationId

        return CorrelationId.from_sequence(1)


class CommandQueryHandlers:
    """Bindet die standardisierten Command-Abfragen an die Query-Pipeline."""

    def __init__(
        self,
        lifecycle: CommandLifecycleService,
        search: CommandSearchService,
        administration: CommandAdministrationService,
    ) -> None:
        self._lifecycle = lifecycle
        self._search = search
        self._administration = administration

    def register(self, pipeline: ProjectQueryPipeline) -> None:
        pipeline.register(QUERY_COMMAND_LIFECYCLE, self.lifecycle)
        pipeline.register(QUERY_COMMAND_SEARCH, self.search)
        pipeline.register(QUERY_COMMAND_DIAGNOSTIC, self.diagnostic)

    def lifecycle(self, query: Query) -> CommandLifecycleView:
        command_id = _business_id(query.parameters, "command_id")
        return self._lifecycle.get(command_id)

    def search(self, query: Query) -> CommandSearchPage:
        parameters = query.parameters
        filters = CommandSearchFilter(
            project_id=_optional_business_id(parameters, "project_id"),
            command_type=_optional_text(parameters, "command_type"),
            state=_optional_state(parameters, "state"),
            processed_from=_optional_datetime(parameters, "processed_from"),
            processed_until=_optional_datetime(parameters, "processed_until"),
            text=_optional_text(parameters, "text"),
        )
        page = _optional_int(parameters, "page", default=1)
        page_size = _optional_int(parameters, "page_size", default=50)
        return self._search.search(filters, page=page, page_size=page_size)

    def diagnostic(self, query: Query) -> CommandExecutionDiagnostic:
        if query.parameters:
            raise ValueError("Die Diagnose-Query akzeptiert keine Parameter.")
        return self._administration.diagnostic()


def _business_id(parameters: Mapping[str, object], name: str) -> BusinessId:
    value = parameters.get(name)
    if value is None:
        raise KeyError(f"Pflichtparameter {name} fehlt.")
    if isinstance(value, BusinessId):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Parameter {name} muss Text oder BusinessId sein.")
    return BusinessId.parse(value)


def _optional_business_id(parameters: Mapping[str, object], name: str) -> BusinessId | None:
    return None if parameters.get(name) is None else _business_id(parameters, name)


def _optional_text(parameters: Mapping[str, object], name: str) -> str | None:
    value = parameters.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"Parameter {name} muss Text sein.")
    return value


def _optional_state(parameters: Mapping[str, object], name: str) -> CommandLifecycleState | None:
    value = parameters.get(name)
    if value is None:
        return None
    if isinstance(value, CommandLifecycleState):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Parameter {name} muss Text oder CommandLifecycleState sein.")
    return CommandLifecycleState(value.strip().upper())


def _optional_datetime(parameters: Mapping[str, object], name: str) -> datetime | None:
    value = parameters.get(name)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise TypeError(f"Parameter {name} muss ISO-8601-Text oder datetime sein.")
    return datetime.fromisoformat(value)


def _optional_int(parameters: Mapping[str, object], name: str, *, default: int) -> int:
    value = parameters.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Parameter {name} muss eine Ganzzahl sein.")
    return value
