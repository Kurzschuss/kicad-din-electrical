"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .application import Command, LocalCommandBus, LocalQueryBus, Query
from .authorization import (
    AuthorizationContext,
    AuthorizationResult,
    AuthorizationService,
    ExceptionRight,
    Role,
)
from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator

__all__ = [
    "AuthorizationContext",
    "AuthorizationResult",
    "AuthorizationService",
    "BusinessId",
    "Command",
    "CorrelationId",
    "DomainEvent",
    "DomainEventCollector",
    "ExceptionRight",
    "InMemoryRepository",
    "LocalCommandBus",
    "LocalEventBus",
    "LocalQueryBus",
    "MessageSeverity",
    "ObjectId",
    "Query",
    "Repository",
    "RepositoryEntity",
    "RepositoryRecord",
    "Result",
    "ResultMessage",
    "Role",
    "RuntimeInfo",
    "ValidationProfile",
    "ValidationResult",
    "ValidationRule",
    "Validator",
    "create_runtime_info",
]
__version__ = "0.8.0"
