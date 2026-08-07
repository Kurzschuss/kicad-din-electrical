from projectos import (
    BreakingCapacity,
    BusinessId,
    CorrelationId,
    MCB,
    NominalCurrent,
    ObjectId,
    PoleCount,
    ProtectionDevicePair,
    RCCB,
    RCCBPoleCount,
    RCCBRatedVoltage,
    RCCBType,
    RatedCurrent,
    RatedVoltage,
    ResidualCurrent,
    TripCharacteristic,
    validate_protection_pair,
)


def make_mcb(*, current: int = 16, voltage: int = 230, poles: int = 1) -> MCB:
    return MCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("MCB-000001"),
        manufacturer="Test",
        product_name="MCB",
        nominal_current=NominalCurrent(current),
        rated_voltage=RatedVoltage(voltage),
        trip_characteristic=TripCharacteristic.B,
        pole_count=PoleCount(poles),
        breaking_capacity=BreakingCapacity(6000),
    )


def make_rccb(*, current: int = 40, voltage: int = 230, poles: int = 2) -> RCCB:
    return RCCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("RCCB-000001"),
        manufacturer="Test",
        product_name="RCCB",
        rated_current=RatedCurrent(current),
        residual_current=ResidualCurrent(30),
        rated_voltage=RCCBRatedVoltage(voltage),
        pole_count=RCCBPoleCount(poles),
        rccb_type=RCCBType.A,
    )


def make_pair(mcb: MCB, rccb: RCCB) -> ProtectionDevicePair:
    return ProtectionDevicePair(BusinessId("PAIR-PROT-000001"), mcb, rccb)


def test_valid_pair_combines_both_domain_results() -> None:
    result = validate_protection_pair(
        make_pair(make_mcb(), make_rccb()),
        correlation_id=CorrelationId.from_sequence(33),
    )

    assert result.is_valid
    assert result.correlation_id == CorrelationId.from_sequence(33)
    assert result.coordination_messages == ()
    assert result.mcb_result.is_valid
    assert result.rccb_result.is_valid


def test_voltage_mismatch_is_rejected() -> None:
    result = validate_protection_pair(make_pair(make_mcb(voltage=230), make_rccb(voltage=400, poles=4)))

    assert not result.is_valid
    assert {str(message.code) for message in result.errors} == {"ERR-PROT-0001"}


def test_mcb_current_must_not_exceed_rccb_current() -> None:
    result = validate_protection_pair(make_pair(make_mcb(current=50), make_rccb(current=40)))

    assert not result.is_valid
    assert "ERR-PROT-0002" in {str(message.code) for message in result.errors}


def test_mcb_pole_count_must_not_exceed_rccb_pole_count() -> None:
    result = validate_protection_pair(
        make_pair(make_mcb(voltage=400, poles=3), make_rccb(voltage=400, poles=2))
    )

    codes = {str(message.code) for message in result.errors}
    assert "ERR-PROT-0003" in codes
    assert "ERR-RCCB-0004" in codes


def test_pair_identifier_prefix_is_required() -> None:
    try:
        ProtectionDevicePair(BusinessId("PAIR-000001"), make_mcb(), make_rccb())
    except ValueError as error:
        assert "PAIR-PROT-" in str(error)
    else:
        raise AssertionError("Ungültige Paar-Kennung wurde akzeptiert.")
