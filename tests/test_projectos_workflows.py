from datetime import datetime, timezone

from projectos import (
    AuthorizationContext,
    AuthorizationService,
    BreakingCapacity,
    BusinessId,
    Command,
    CorrelationId,
    InMemoryAuditRepository,
    InMemoryRepository,
    LocalCommandBus,
    MCB,
    NominalCurrent,
    ObjectId,
    PERM_PROTECTION_REGISTER,
    PoleCount,
    ProtectionDevicePair,
    RCCB,
    RCCBPoleCount,
    RCCBRatedVoltage,
    RCCBType,
    REGISTER_PROTECTION_PAIR,
    RatedCurrent,
    RatedVoltage,
    RegisterProtectionPairHandler,
    ResidualCurrent,
    Role,
    SimulationContext,
    SimulationTrace,
    TripCharacteristic,
)

NOW = datetime(2026, 8, 6, 8, 30, tzinfo=timezone.utc)


def make_pair(*, mcb_current: int = 16) -> ProtectionDevicePair:
    mcb = MCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("MCB-000001"),
        manufacturer="ProjectOS",
        product_name="MCB Test",
        nominal_current=NominalCurrent(mcb_current),
        rated_voltage=RatedVoltage(230),
        trip_characteristic=TripCharacteristic.B,
        pole_count=PoleCount(1),
        breaking_capacity=BreakingCapacity(6000),
    )
    rccb = RCCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("RCCB-000001"),
        manufacturer="ProjectOS",
        product_name="RCCB Test",
        rated_current=RatedCurrent(40),
        residual_current=ResidualCurrent(30),
        rated_voltage=RCCBRatedVoltage(230),
        pole_count=RCCBPoleCount(2),
        rccb_type=RCCBType.A,
    )
    return ProtectionDevicePair(BusinessId("PAIR-PROT-000001"), mcb, rccb)


def make_command(pair: ProtectionDevicePair, *, simulation_mode: bool = False) -> Command:
    return Command(
        command_id=BusinessId("CMD-00000001"),
        command_type=REGISTER_PROTECTION_PAIR,
        correlation_id=CorrelationId.from_sequence(1),
        issued_at=NOW,
        payload={
            "pair": pair,
            "authorization_context": AuthorizationContext(
                user_id=BusinessId("USR-000001"),
                role_ids=frozenset({BusinessId("ROLE-ENGINEERING")}),
            ),
            "acting_role": BusinessId("ROLE-ENGINEERING"),
            "audit_id": BusinessId("AUD-PROT-000001"),
            "reason": "Freigegebenes End-to-End-Testszenario",
            "simulation_mode": simulation_mode,
        },
    )


def make_handler(*, authorized: bool = True, trace: SimulationTrace | None = None):
    role = Role(
        BusinessId("ROLE-ENGINEERING"),
        frozenset({PERM_PROTECTION_REGISTER}) if authorized else frozenset(),
    )
    mcb_repository = InMemoryRepository[MCB]()
    rccb_repository = InMemoryRepository[RCCB]()
    audit_repository = InMemoryAuditRepository()
    handler = RegisterProtectionPairHandler(
        mcb_repository=mcb_repository,
        rccb_repository=rccb_repository,
        authorization=AuthorizationService(roles={role.role_id: role}),
        audit_repository=audit_repository,
        simulation_trace=trace,
    )
    return handler, mcb_repository, rccb_repository, audit_repository


def test_end_to_end_registers_valid_pair_and_writes_audit() -> None:
    handler, mcb_repository, rccb_repository, audit_repository = make_handler()
    bus = LocalCommandBus()
    bus.register(REGISTER_PROTECTION_PAIR, handler)

    result = bus.dispatch(make_command(make_pair()))

    assert result.is_success
    assert result.value is not None
    assert result.value.simulated is False
    assert len(mcb_repository.list_all()) == 1
    assert len(rccb_repository.list_all()) == 1
    assert len(audit_repository.all()) == 1
    assert audit_repository.verify_integrity()


def test_unauthorized_command_changes_nothing() -> None:
    handler, mcb_repository, rccb_repository, audit_repository = make_handler(authorized=False)

    result = handler(make_command(make_pair()))

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-AUTH-0001"
    assert not mcb_repository.list_all()
    assert not rccb_repository.list_all()
    assert not audit_repository.all()


def test_invalid_pair_is_not_persisted() -> None:
    handler, mcb_repository, rccb_repository, audit_repository = make_handler()

    result = handler(make_command(make_pair(mcb_current=63)))

    assert not result.is_success
    assert any(str(message.code) == "ERR-PROT-0002" for message in result.errors)
    assert not mcb_repository.list_all()
    assert not rccb_repository.list_all()
    assert not audit_repository.all()


def test_simulation_records_trace_without_persistence_or_audit() -> None:
    trace = SimulationTrace(
        SimulationContext(
            simulation_id=BusinessId("SIM-000001"),
            scenario_id=BusinessId("SCN-PROT-000001"),
            correlation_id=CorrelationId.from_sequence(1),
            started_at=NOW,
        )
    )
    handler, mcb_repository, rccb_repository, audit_repository = make_handler(trace=trace)

    result = handler(make_command(make_pair(), simulation_mode=True))

    assert result.is_success
    assert result.value is not None and result.value.simulated
    assert not mcb_repository.list_all()
    assert not rccb_repository.list_all()
    assert not audit_repository.all()
    assert trace.entries[0].reference == "protection_pair_validated"
