"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .application import Command, LocalCommandBus, LocalQueryBus, Query
from .audit import AuditEntry, InMemoryAuditRepository
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService, ExceptionRight, Role
from .device_persistence import (
    create_mcb_sqlite_repository,
    create_rccb_sqlite_repository,
    decode_mcb,
    decode_rccb,
    encode_mcb,
    encode_rccb,
)
from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic, create_mcb_validation_profile, validate_mcb
from .outbox import AtomicOutboxResult, OutboxMessage, SQLiteOutboxRepository, add_with_outbox
from .outbox_admin import DeadLetterRecovery, OutboxAdministrationService, OutboxDiagnostic
from .outbox_delivery import (
    DeliveryState,
    DeliveryStatus,
    OutboxProcessingResult,
    OutboxProcessor,
    SQLiteDeliveryRepository,
)
from .protection import ProtectionDevicePair, ProtectionValidationResult, validate_protection_pair
from .rccb import RCCB, RCCBPoleCount, RCCBRatedVoltage, RCCBType, RatedCurrent, ResidualCurrent, create_rccb_validation_profile, validate_rccb
from .release import ReleaseManifest, SemanticVersion, VersionBump
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .simulation import SimulationClock, SimulationContext, SimulationTrace, SimulationTraceEntry
from .sqlite import SQLiteJsonRepository, SQLiteRepositoryConfig, SQLiteUnitOfWork
from .sqlite_audit import AtomicPersistenceResult, SQLiteAuditRepository, add_with_audit
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator
from .workflows import (
    PERM_PROTECTION_REGISTER,
    REGISTER_PROTECTION_PAIR,
    ProtectionRegistrationResult,
    RegisterProtectionPairHandler,
)

__all__ = [
    "AtomicOutboxResult", "AtomicPersistenceResult", "AuditEntry", "AuthorizationContext",
    "AuthorizationResult", "AuthorizationService", "BreakingCapacity", "BusinessId", "Command",
    "CorrelationId", "DeadLetterRecovery", "DeliveryState", "DeliveryStatus", "DomainEvent",
    "DomainEventCollector", "ExceptionRight", "InMemoryAuditRepository", "InMemoryRepository",
    "LocalCommandBus", "LocalEventBus", "LocalQueryBus", "MCB", "MessageSeverity",
    "NominalCurrent", "ObjectId", "OutboxAdministrationService", "OutboxDiagnostic",
    "OutboxMessage", "OutboxProcessingResult", "OutboxProcessor", "PERM_PROTECTION_REGISTER",
    "PoleCount", "ProtectionDevicePair", "ProtectionRegistrationResult",
    "ProtectionValidationResult", "Query", "RCCB", "RCCBPoleCount", "RCCBRatedVoltage",
    "RCCBType", "REGISTER_PROTECTION_PAIR", "RatedCurrent", "RatedVoltage",
    "RegisterProtectionPairHandler", "ReleaseManifest", "Repository", "RepositoryEntity",
    "RepositoryRecord", "ResidualCurrent", "Result", "ResultMessage", "Role", "RuntimeInfo",
    "SQLiteAuditRepository", "SQLiteDeliveryRepository", "SQLiteJsonRepository",
    "SQLiteOutboxRepository", "SQLiteRepositoryConfig", "SQLiteUnitOfWork", "SemanticVersion",
    "SimulationClock", "SimulationContext", "SimulationTrace", "SimulationTraceEntry",
    "TripCharacteristic", "ValidationProfile", "ValidationResult", "ValidationRule", "Validator",
    "VersionBump", "add_with_audit", "add_with_outbox", "create_mcb_sqlite_repository",
    "create_mcb_validation_profile", "create_rccb_sqlite_repository",
    "create_rccb_validation_profile", "create_runtime_info", "decode_mcb", "decode_rccb",
    "encode_mcb", "encode_rccb", "validate_mcb", "validate_protection_pair", "validate_rccb",
]
__version__ = "0.21.0"
