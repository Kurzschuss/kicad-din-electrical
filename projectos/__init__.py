"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .application import Command, LocalCommandBus, LocalQueryBus, Query
from .audit import AuditEntry, InMemoryAuditRepository
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService, ExceptionRight, Role
from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic, create_mcb_validation_profile, validate_mcb
from .protection import ProtectionDevicePair, ProtectionValidationResult, validate_protection_pair
from .rccb import RCCB, RCCBPoleCount, RCCBRatedVoltage, RCCBType, RatedCurrent, ResidualCurrent, create_rccb_validation_profile, validate_rccb
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .simulation import SimulationClock, SimulationContext, SimulationTrace, SimulationTraceEntry
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator
from .workflows import (
    PERM_PROTECTION_REGISTER,
    REGISTER_PROTECTION_PAIR,
    ProtectionRegistrationResult,
    RegisterProtectionPairHandler,
)

__all__ = [
    "AuditEntry", "AuthorizationContext", "AuthorizationResult", "AuthorizationService",
    "BreakingCapacity", "BusinessId", "Command", "CorrelationId", "DomainEvent",
    "DomainEventCollector", "ExceptionRight", "InMemoryAuditRepository", "InMemoryRepository",
    "LocalCommandBus", "LocalEventBus", "LocalQueryBus", "MCB", "MessageSeverity",
    "NominalCurrent", "ObjectId", "PERM_PROTECTION_REGISTER", "PoleCount",
    "ProtectionDevicePair", "ProtectionRegistrationResult", "ProtectionValidationResult", "Query",
    "RCCB", "RCCBPoleCount", "RCCBRatedVoltage", "RCCBType", "REGISTER_PROTECTION_PAIR",
    "RatedCurrent", "RatedVoltage", "RegisterProtectionPairHandler", "Repository",
    "RepositoryEntity", "RepositoryRecord", "ResidualCurrent", "Result", "ResultMessage",
    "Role", "RuntimeInfo", "SimulationClock", "SimulationContext", "SimulationTrace",
    "SimulationTraceEntry", "TripCharacteristic", "ValidationProfile", "ValidationResult",
    "ValidationRule", "Validator", "create_mcb_validation_profile",
    "create_rccb_validation_profile", "create_runtime_info", "validate_mcb",
    "validate_protection_pair", "validate_rccb",
]
__version__ = "0.14.0"
