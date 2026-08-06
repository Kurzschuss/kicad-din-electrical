"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator

__all__ = [
    "BusinessId",
    "CorrelationId",
    "DomainEvent",
    "DomainEventCollector",
    "InMemoryRepository",
    "LocalEventBus",
    "MessageSeverity",
    "ObjectId",
    "Repository",
    "RepositoryEntity",
    "RepositoryRecord",
    "Result",
    "ResultMessage",
    "RuntimeInfo",
    "ValidationProfile",
    "ValidationResult",
    "ValidationRule",
    "Validator",
    "create_runtime_info",
]
__version__ = "0.6.0"
