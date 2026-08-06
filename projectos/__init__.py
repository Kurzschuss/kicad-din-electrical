"""ProjectOS-Kernpaket für kicad-din-electrical."""

from .application import Command, LocalCommandBus, LocalQueryBus, Query
from .audit import AuditEntry, InMemoryAuditRepository
from .authorization import AuthorizationContext, AuthorizationResult, AuthorizationService, ExceptionRight, Role
from .device_catalog import CatalogDevice, CatalogDeviceStatus, DeviceCategory, DeviceProperty
from .device_persistence import create_mcb_sqlite_repository, create_rccb_sqlite_repository, decode_mcb, decode_rccb, encode_mcb, encode_rccb
from .events import DomainEvent, DomainEventCollector, LocalEventBus
from .identifiers import BusinessId, CorrelationId, ObjectId
from .identity_persistence import SQLiteIdentityRepository, UserAccount
from .kicad_assets import KiCadAssetReference, KiCadAssetStatus, KiCadAssetTargetType, KiCadAssetType, KiCadLibraryReference, ensure_unique_kicad_asset
from .manufacturer import Manufacturer, ManufacturerReference, ManufacturerStatus, ProductSeries, ensure_unique_series_name
from .manufacturer_product import ManufacturerProduct, ProductIdentifier, ProductIdentifierType, ProductStatus, ensure_unique_product_identifiers
from .mcb import BreakingCapacity, MCB, NominalCurrent, PoleCount, RatedVoltage, TripCharacteristic, create_mcb_validation_profile, validate_mcb
from .outbox import AtomicOutboxResult, OutboxMessage, SQLiteOutboxRepository, add_with_outbox
from .outbox_admin import DeadLetterRecovery, OutboxAdministrationService, OutboxDiagnostic
from .outbox_authorization import AuthorizedDeadLetterRecovery, AuthorizedOutboxAdministrationService, PERM_OUTBOX_DEAD_LETTER_RECOVER
from .outbox_delivery import DeliveryState, DeliveryStatus, OutboxProcessingResult, OutboxProcessor, SQLiteDeliveryRepository
from .project_authority import ProjectAuthorityResolution, ProjectAuthorityService
from .project_authorization import ProjectActionAuthorizationResult, ProjectActionAuthorizationService, SQLiteProjectAuthorityPolicyRepository
from .project_command_admin import CommandAdministrationService, CommandExecutionDiagnostic, CommandRecoveryRecord
from .project_command_authorization import AuthorizedCommandAdministrationService, AuthorizedCommandRecovery, PERM_PROJECT_COMMAND_RECOVER
from .project_command_history import CommandExecutionRecord, CommandExecutionStatus, IdempotentProjectCommandPipeline, IdempotentProjectCommandResult, SQLiteCommandExecutionRepository, command_fingerprint
from .project_command_lifecycle import CommandLifecycleService, CommandLifecycleState, CommandLifecycleView
from .project_command_retry import CommandRetryRecord, RecoveredCommandExecutionResult, RecoveredCommandExecutionService
from .project_command_search import CommandSearchFilter, CommandSearchItem, CommandSearchPage, CommandSearchService
from .project_commands import ProjectCommandDefinition, ProjectCommandExecutionResult, ProjectCommandPipeline
from .project_execution import AuditedProjectActionResult, AuditedProjectActionService
from .project_queries import CommandQueryHandlers, ProjectQueryExecutionResult, ProjectQueryPipeline, QUERY_COMMAND_DIAGNOSTIC, QUERY_COMMAND_LIFECYCLE, QUERY_COMMAND_SEARCH
from .project_query_audit import AuditedProjectQueryPipeline, AuditedProjectQueryResult, PERM_PROJECT_QUERY_UNMAPPED
from .project_query_authorization import AuthorizedProjectQueryPipeline, AuthorizedProjectQueryResult, PERM_PROJECT_COMMAND_DIAGNOSTIC_READ, PERM_PROJECT_COMMAND_LIFECYCLE_READ, PERM_PROJECT_COMMAND_SEARCH
from .project_responsibilities import ProjectResponsibility, ProjectResponsibilitySnapshot, ProjectResponsibilityType, SQLiteProjectResponsibilityRepository
from .protection import ProtectionDevicePair, ProtectionValidationResult, validate_protection_pair
from .query_audit_search import QueryAuditFilter, QueryAuditItem, QueryAuditPage, QueryAuditSearchService, QueryAuditStatistics
from .rccb import RCCB, RCCBPoleCount, RCCBRatedVoltage, RCCBType, RatedCurrent, ResidualCurrent, create_rccb_validation_profile, validate_rccb
from .release import ReleaseManifest, SemanticVersion, VersionBump
from .repositories import InMemoryRepository, Repository, RepositoryEntity, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .runtime import RuntimeInfo, create_runtime_info
from .simulation import SimulationClock, SimulationContext, SimulationTrace, SimulationTraceEntry
from .sqlite import SQLiteJsonRepository, SQLiteRepositoryConfig, SQLiteUnitOfWork
from .sqlite_audit import AtomicPersistenceResult, SQLiteAuditRepository, add_with_audit
from .standards import ConformityReference, ConformityStatus, ConformityTargetType, StandardBody, StandardReference, StandardStatus, ensure_unique_standard_edition
from .validation import ValidationProfile, ValidationResult, ValidationRule, Validator
from .workflows import PERM_PROTECTION_REGISTER, REGISTER_PROTECTION_PAIR, ProtectionRegistrationResult, RegisterProtectionPairHandler

__all__ = [name for name in globals() if not name.startswith("_")]
__version__ = "0.43.0"
