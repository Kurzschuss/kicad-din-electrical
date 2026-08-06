"""Ausführbarer End-to-End-Anwendungsfall für ProjectOS-Schutzgeräte."""

from __future__ import annotations

from dataclasses import dataclass

from .application import Command
from .audit import AuditEntry, InMemoryAuditRepository
from .authorization import AuthorizationContext, AuthorizationService
from .identifiers import BusinessId
from .mcb import MCB
from .protection import ProtectionDevicePair, ProtectionValidationResult, validate_protection_pair
from .rccb import RCCB
from .repositories import InMemoryRepository, RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage
from .simulation import SimulationTrace

REGISTER_PROTECTION_PAIR = "protection.pair.register"
PERM_PROTECTION_REGISTER = BusinessId("PERM-PROT-REGISTER")


@dataclass(frozen=True, slots=True)
class ProtectionRegistrationResult:
    """Ergebnis des vollständigen Schutzgeräte-Anwendungsfalls."""

    pair_id: BusinessId
    validation: ProtectionValidationResult
    mcb_record: RepositoryRecord[MCB] | None
    rccb_record: RepositoryRecord[RCCB] | None
    audit_id: BusinessId | None
    simulated: bool


class RegisterProtectionPairHandler:
    """Koordiniert Autorisierung, Validierung, Speicherung, Audit und Simulation."""

    def __init__(
        self,
        *,
        mcb_repository: InMemoryRepository[MCB],
        rccb_repository: InMemoryRepository[RCCB],
        authorization: AuthorizationService,
        audit_repository: InMemoryAuditRepository,
        simulation_trace: SimulationTrace | None = None,
    ) -> None:
        self._mcb_repository = mcb_repository
        self._rccb_repository = rccb_repository
        self._authorization = authorization
        self._audit_repository = audit_repository
        self._simulation_trace = simulation_trace

    def __call__(self, command: Command) -> Result[ProtectionRegistrationResult]:
        if command.command_type != REGISTER_PROTECTION_PAIR:
            return self._failure("ERR-APP-0034", "Der Command-Typ wird von diesem Handler nicht unterstützt.", command)

        pair = command.payload.get("pair")
        context = command.payload.get("authorization_context")
        actor_role = command.payload.get("acting_role")
        audit_id = command.payload.get("audit_id")
        reason = command.payload.get("reason")
        simulation_mode = command.payload.get("simulation_mode", False)

        if not isinstance(pair, ProtectionDevicePair):
            return self._failure("ERR-APP-0035", "Der Command benötigt ein ProtectionDevicePair.", command)
        if not isinstance(context, AuthorizationContext):
            return self._failure("ERR-APP-0036", "Der Command benötigt einen AuthorizationContext.", command)
        if not isinstance(actor_role, BusinessId):
            return self._failure("ERR-APP-0037", "Der Command benötigt eine handelnde Rolle.", command)
        if not isinstance(audit_id, BusinessId):
            return self._failure("ERR-APP-0038", "Der Command benötigt eine Audit-Kennung.", command)
        if not isinstance(reason, str) or not reason.strip():
            return self._failure("ERR-APP-0039", "Der Command benötigt einen Änderungsgrund.", command)
        if not isinstance(simulation_mode, bool):
            return self._failure("ERR-APP-0040", "simulation_mode muss boolesch sein.", command)

        authorization = self._authorization.authorize(
            context,
            PERM_PROTECTION_REGISTER,
            at=command.issued_at,
        )
        if not authorization.allowed:
            return self._failure("ERR-AUTH-0001", authorization.reason, command)

        validation = validate_protection_pair(pair, correlation_id=command.correlation_id)
        if not validation.is_valid:
            return Result.failure(*validation.errors, correlation_id=command.correlation_id)

        if simulation_mode:
            if self._simulation_trace is not None:
                self._simulation_trace.record(
                    occurred_at=command.issued_at,
                    category="APPLICATION",
                    reference="protection_pair_validated",
                    data={"pair_id": str(pair.pair_id), "valid": True},
                )
            return Result.success(
                ProtectionRegistrationResult(
                    pair_id=pair.pair_id,
                    validation=validation,
                    mcb_record=None,
                    rccb_record=None,
                    audit_id=None,
                    simulated=True,
                ),
                messages=validation.warnings,
                correlation_id=command.correlation_id,
            )

        mcb_result = self._mcb_repository.add(pair.mcb)
        if not mcb_result.is_success:
            return Result.failure(*mcb_result.errors, correlation_id=command.correlation_id)

        rccb_result = self._rccb_repository.add(pair.rccb)
        if not rccb_result.is_success:
            assert mcb_result.value is not None
            self._mcb_repository.delete(pair.mcb.object_id, expected_revision=mcb_result.value.revision)
            return Result.failure(*rccb_result.errors, correlation_id=command.correlation_id)

        assert mcb_result.value is not None and rccb_result.value is not None
        entries = self._audit_repository.all()
        previous_hash = entries[-1].entry_hash if entries else ""
        audit_entry = AuditEntry(
            audit_id=audit_id,
            occurred_at=command.issued_at,
            actor_id=context.user_id,
            acting_role=actor_role,
            permission_id=PERM_PROTECTION_REGISTER,
            object_id=pair.mcb.object_id,
            object_business_id=pair.pair_id,
            action="protection_pair_registered",
            reason=reason,
            correlation_id=command.correlation_id,
            new_values={
                "mcb": str(pair.mcb.business_id),
                "rccb": str(pair.rccb.business_id),
            },
            previous_hash=previous_hash,
        )
        self._audit_repository.append(audit_entry)

        return Result.success(
            ProtectionRegistrationResult(
                pair_id=pair.pair_id,
                validation=validation,
                mcb_record=mcb_result.value,
                rccb_record=rccb_result.value,
                audit_id=audit_entry.audit_id,
                simulated=False,
            ),
            messages=validation.warnings,
            correlation_id=command.correlation_id,
        )

    @staticmethod
    def _failure(code: str, text: str, command: Command) -> Result[ProtectionRegistrationResult]:
        return Result.failure(
            ResultMessage(BusinessId(code), MessageSeverity.ERROR, text),
            correlation_id=command.correlation_id,
        )
