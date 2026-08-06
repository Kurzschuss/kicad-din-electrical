"""Projektbezogene Leseberechtigungen für die ProjectOS-Query-Pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from .application import Query
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService
from .identifiers import BusinessId
from .project_queries import (
    QUERY_COMMAND_DIAGNOSTIC,
    QUERY_COMMAND_LIFECYCLE,
    QUERY_COMMAND_SEARCH,
    ProjectQueryExecutionResult,
    ProjectQueryPipeline,
)
from .results import MessageSeverity, Result, ResultMessage

PERM_PROJECT_COMMAND_LIFECYCLE_READ = BusinessId("PERM-PROJECT-COMMAND-LIFECYCLE-READ")
PERM_PROJECT_COMMAND_SEARCH = BusinessId("PERM-PROJECT-COMMAND-SEARCH")
PERM_PROJECT_COMMAND_DIAGNOSTIC_READ = BusinessId("PERM-PROJECT-COMMAND-DIAGNOSTIC-READ")

_QUERY_PERMISSIONS = {
    QUERY_COMMAND_LIFECYCLE: PERM_PROJECT_COMMAND_LIFECYCLE_READ,
    QUERY_COMMAND_SEARCH: PERM_PROJECT_COMMAND_SEARCH,
    QUERY_COMMAND_DIAGNOSTIC: PERM_PROJECT_COMMAND_DIAGNOSTIC_READ,
}


@dataclass(frozen=True, slots=True)
class AuthorizedProjectQueryResult:
    """Ergebnis einer autorisierten ProjectOS-Query."""

    authorization: AuthorizationResult
    execution: ProjectQueryExecutionResult
    permission: BusinessId


class AuthorizedProjectQueryPipeline:
    """Prüft Leseberechtigungen vor der Ausführung registrierter Queries."""

    def __init__(
        self,
        authorization: AuthorizationService,
        pipeline: ProjectQueryPipeline,
    ) -> None:
        self._authorization = authorization
        self._pipeline = pipeline

    def execute(
        self,
        query: Query,
        *,
        context: AuthorizationContext,
    ) -> Result[AuthorizedProjectQueryResult]:
        permission = _QUERY_PERMISSIONS.get(query.query_type)
        if permission is None:
            return self._failure(
                query,
                "ERR-PRJ-QRY-0003",
                "Für den Query-Typ ist keine Leseberechtigung konfiguriert.",
            )

        project_error = self._validate_project_scope(query, context)
        if project_error is not None:
            return project_error

        decision = self._authorization.authorize(
            context,
            permission,
            at=query.requested_at,
        )
        if not decision.allowed:
            return self._failure(
                query,
                "ERR-PRJ-QRY-0004",
                f"Query nicht autorisiert: {decision.reason}",
                permission=str(permission),
            )

        executed = self._pipeline.execute(query)
        if not executed.is_success:
            return Result.failure(*executed.messages, correlation_id=query.correlation_id)
        assert executed.value is not None
        return Result.success(
            AuthorizedProjectQueryResult(
                authorization=decision,
                execution=executed.value,
                permission=permission,
            ),
            correlation_id=query.correlation_id,
        )

    @staticmethod
    def _validate_project_scope(
        query: Query,
        context: AuthorizationContext,
    ) -> Result[AuthorizedProjectQueryResult] | None:
        if query.query_type not in {QUERY_COMMAND_LIFECYCLE, QUERY_COMMAND_SEARCH}:
            return None
        if context.project_id is None:
            return AuthorizedProjectQueryPipeline._failure(
                query,
                "ERR-PRJ-QRY-0005",
                "Die projektbezogene Query benötigt einen Projektkontext.",
            )
        requested_project = query.parameters.get("project_id")
        if requested_project is None:
            return AuthorizedProjectQueryPipeline._failure(
                query,
                "ERR-PRJ-QRY-0006",
                "Die projektbezogene Query benötigt den Parameter project_id.",
            )
        try:
            project_id = requested_project if isinstance(requested_project, BusinessId) else BusinessId.parse(str(requested_project))
        except (TypeError, ValueError):
            return AuthorizedProjectQueryPipeline._failure(
                query,
                "ERR-PRJ-QRY-0006",
                "Der Parameter project_id ist ungültig.",
            )
        if project_id != context.project_id:
            return AuthorizedProjectQueryPipeline._failure(
                query,
                "ERR-PRJ-QRY-0007",
                "Der angeforderte Projektbereich stimmt nicht mit dem Autorisierungskontext überein.",
            )
        return None

    @staticmethod
    def _failure(
        query: Query,
        code: str,
        text: str,
        **parameters: object,
    ) -> Result[AuthorizedProjectQueryResult]:
        return Result.failure(
            ResultMessage(
                BusinessId(code),
                MessageSeverity.ERROR,
                text,
                parameters=parameters,
            ),
            correlation_id=query.correlation_id,
        )
