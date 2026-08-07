"""Standardisierte projektbezogene Command-Pipeline für ProjectOS."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

from .application import Command
from .identifiers import BusinessId, ObjectId
from .project_execution import AuditedProjectActionResult, AuditedProjectActionService
from .results import MessageSeverity, Result, ResultMessage

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ProjectCommandDefinition:
    """Verbindliche Metadaten eines projektbezogenen Commands."""

    command_type: str
    permission: BusinessId
    audit_action: str

    def __post_init__(self) -> None:
        command_type = self.command_type.strip().lower()
        parts = command_type.split(".")
        if len(parts) < 3 or any(not part.replace("_", "").isalnum() for part in parts):
            raise ValueError("Command-Typ muss dem Schema <domäne>.<objekt>.<aktion> entsprechen.")
        action = self.audit_action.strip()
        if not action:
            raise ValueError("Eine Command-Definition benötigt eine Audit-Aktion.")
        object.__setattr__(self, "command_type", command_type)
        object.__setattr__(self, "audit_action", action)


@dataclass(frozen=True, slots=True)
class ProjectCommandExecutionResult(Generic[T]):
    """Einheitlicher Ergebnisvertrag einer projektbezogenen Command-Ausführung."""

    command: Command
    project_id: BusinessId
    execution: AuditedProjectActionResult[T]

    @property
    def executed(self) -> bool:
        return self.execution.executed

    @property
    def value(self) -> T | None:
        return self.execution.value


ProjectCommandHandler = Callable[[Command], object]


class ProjectCommandPipeline:
    """Registriert und verarbeitet projektbezogene Commands deterministisch."""

    def __init__(self, actions: AuditedProjectActionService) -> None:
        self._actions = actions
        self._definitions: dict[str, ProjectCommandDefinition] = {}
        self._handlers: dict[str, ProjectCommandHandler] = {}

    def register(
        self,
        definition: ProjectCommandDefinition,
        handler: Callable[[Command], T],
    ) -> None:
        if definition.command_type in self._handlers:
            raise ValueError(
                f"Für {definition.command_type} ist bereits ein Projekt-Command-Handler registriert."
            )
        self._definitions[definition.command_type] = definition
        self._handlers[definition.command_type] = cast(ProjectCommandHandler, handler)

    def dispatch(
        self,
        command: Command,
        *,
        project_id: BusinessId,
        project_object_id: ObjectId,
        audit_id: BusinessId,
        reason: str,
        unavailable_user_ids: frozenset[BusinessId] = frozenset(),
    ) -> Result[ProjectCommandExecutionResult[object]]:
        definition = self._definitions.get(command.command_type)
        handler = self._handlers.get(command.command_type)
        if definition is None or handler is None:
            return Result.failure(
                ResultMessage(
                    BusinessId("ERR-PRJ-CMD-0001"),
                    MessageSeverity.ERROR,
                    f"Kein projektbezogener Command-Handler für {command.command_type} registriert.",
                ),
                correlation_id=command.correlation_id,
            )

        normalized_reason = reason.strip()
        if not normalized_reason:
            return Result.failure(
                ResultMessage(
                    BusinessId("ERR-PRJ-CMD-0002"),
                    MessageSeverity.ERROR,
                    "Die Command-Ausführung benötigt eine Begründung.",
                ),
                correlation_id=command.correlation_id,
            )

        execution = self._actions.execute(
            project_id,
            definition.permission,
            at=command.issued_at,
            audit_id=audit_id,
            correlation_id=command.correlation_id,
            project_object_id=project_object_id,
            action=definition.audit_action,
            reason=normalized_reason,
            unavailable_user_ids=unavailable_user_ids,
            new_values={
                "command_id": str(command.command_id),
                "command_type": command.command_type,
                "expected_revision": command.expected_revision,
            },
            operation=lambda: handler(command),
        )
        if not execution.authorization.allowed:
            return Result.failure(
                ResultMessage(
                    BusinessId("ERR-PRJ-CMD-0003"),
                    MessageSeverity.ERROR,
                    execution.authorization.reason,
                    parameters={
                        "project_id": str(project_id),
                        "command_type": command.command_type,
                    },
                ),
                correlation_id=command.correlation_id,
            )

        return Result.success(
            ProjectCommandExecutionResult(command, project_id, execution),
            correlation_id=command.correlation_id,
        )
