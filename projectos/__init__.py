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
from .identity_persistence import SQLiteIdentityRepository, UserAccount
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic, create_mcb_validation_profile, validate_mcb
from .outbox import AtomicOutboxResult, OutboxMessage, SQLiteOutboxRepository, add_with_outbox
from .outbox_admin import DeadLetterRecovery, OutboxAdministrationService, OutboxDiagnostic
from .outbox_authorization import (
    AuthorizedDeadLetterRecovery,
    AuthorizedOutboxAdministrationService,
    PERM_OUTBOX_DEAD_LETTER_RECOVER,
)
from .outbox_delivery import (
    DeliveryState,
    DeliveryStatus,
    OutboxProcessingResult,
    OutboxProcessor,
    SQLiteDeliveryRepository,
)
from .project_authority import ProjectAuthorityResolution, ProjectAuthorityService
from .project_authorization import (
    ProjectActionAuthorizationResult,
    ProjectActionAuthorizationService,
    SQLiteProjectAuthorityPolicyRepository,
)
from .project_command_admin import (
    CommandAdministrationService,
    CommandExecutionDiagnostic,
    CommandRecoveryRecord,
)
from .project_command_history import (
    CommandExecutionRecord,
    CommandExecutionStatus,
    IdempotentProjectCommandPipeline,
    IdempotentProjectCommandResult,
    SQLiteCommandExecutionRepository,
    command_fingerprint,
)
from .project_commands import (
    ProjectCommandDefinition,
    ProjectCommandExecutionResult,
    ProjectCommandPipeline,
)
from .project_execution import AuditedProjectActionResult, AuditedProjectActionService
from .project_responsibilities import (
    ProjectResponsibility,
    ProjectResponsibilitySnapshot,
    ProjectResponsibilityType,
    SQLiteProjectResponsibilityRepository,
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
    "AtomicOutboxResult", "AtomicPersistenceResult", "AuditEntry", "AuditedProjectActionResult",
    "AuditedProjectActionService", "AuthorizationContext", "AuthorizationResult",
    "AuthorizationService", "AuthorizedDeadLetterRecovery", "AuthorizedOutboxAdministrationService",
    "BreakingCapacity", "BusinessId", "Command", "CommandAdministrationService",
    "CommandExecutionDiagnostic", "CommandExecutionRecord", "CommandExecutionStatus",
    "CommandRecoveryRecord", "CorrelationId", "DeadLetterRecovery", "DeliveryState",
    "DeliveryStatus", "DomainEvent", "DomainEventCollector", "ExceptionRight",
    "IdempotentProjectCommandPipeline", "IdempotentProjectCommandResult",
    "InMemoryAuditRepository", "InMemoryRepository", "LocalCommandBus", "LocalEventBus",
    "LocalQueryBus", "MCB", "MessageSeverity", "NominalCurrent", "ObjectId",
    "OutboxAdministrationService", "OutboxDiagnostic", "OutboxMessage", "OutboxProcessingResult",
    "OutboxProcessor", "PERM_OUTBOX_DEAD_LETTER_RECOVER", "PERM_PROTECTION_REGISTER",
    "PoleCount", "ProjectActionAuthorizationResult", "ProjectActionAuthorizationService",
    "ProjectAuthorityResolution", "ProjectAuthorityService", "ProjectCommandDefinition",
    "ProjectCommandExecutionResult", "ProjectCommandPipeline", "ProjectResponsibility",
    "ProjectResponsibilitySnapshot", "ProjectResponsibilityType", "ProtectionDevicePair",
    "ProtectionRegistrationResult", "ProtectionValidationResult", "Query", "RCCB",
    "RCCBPoleCount", "RCCBRatedVoltage", "RCCBType", "REGISTER_PROTECTION_PAIR",
    "RatedCurrent", "RatedVoltage", "RegisterProtectionPairHandler", "ReleaseManifest",
    "Repository", "RepositoryEntity", "RepositoryRecord", "ResidualCurrent", "Result",
    "ResultMessage", "Role", "RuntimeInfo", "SQLiteAuditRepository",
    "SQLiteCommandExecutionRepository", "SQLiteDeliveryRepository", "SQLiteIdentityRepository",
    "SQLiteJsonRepository", "SQLiteOutboxRepository", "SQLiteProjectAuthorityPolicyRepository",
    "SQLiteProjectResponsibilityRepository", "SQLiteRepositoryConfig", "SQLiteUnitOfWork",
    "SemanticVersion", "SimulationClock", "SimulationContext", "SimulationTrace",
    "SimulationTraceEntry", "TripCharacteristic", "UserAccount", "ValidationProfile",
    "ValidationResult", "ValidationRule", "Validator", "VersionBump", "add_with_audit",
    "add_with_outbox", "command_fingerprint", "create_mcb_sqlite_repository",
    "create_mcb_validation_profile", "create_rccb_sqlite_repository",
    "create_rccb_validation_profile", "create_runtime_info", "decode_mcb", "decode_rccb",
    "encode_mcb", "encode_rccb", "validate_mcb", "validate_protection_pair", "validate_rccb",
]
__version__ = "0.30.0"
