"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .application import Command, LocalCommandBus, LocalQueryBus, Query
from .audit import AuditEntry, InMemoryAuditRepository
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService, ExceptionRight, Role
from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic, create_mcb_validation_profile, validate_mcb
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .simulation import SimulationClock, SimulationContext, SimulationTrace, SimulationTraceEntry
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator

__all__ = [
    "AuditEntry", "AuthorizationContext", "AuthorizationResult", "AuthorizationService",
    "BreakingCapacity", "BusinessId", "Command", "CorrelationId", "DomainEvent",
    "DomainEventCollector", "ExceptionRight", "InMemoryAuditRepository", "InMemoryRepository",
    "LocalCommandBus", "LocalEventBus", "LocalQueryBus", "MCB", "MessageSeverity",
    "NominalCurrent", "ObjectId", "PoleCount", "Query", "RatedVoltage", "Repository",
    "RepositoryEntity", "RepositoryRecord", "Result", "ResultMessage", "Role", "RuntimeInfo",
    "SimulationClock", "SimulationContext", "SimulationTrace", "SimulationTraceEntry",
    "TripCharacteristic", "ValidationProfile", "ValidationResult", "ValidationRule", "Validator",
    "create_mcb_validation_profile", "create_runtime_info", "validate_mcb",
]
__version__ = "0.11.0"
