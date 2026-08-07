from dataclasses import FrozenInstanceError

import pytest

from projectos import (
    BreakingCapacity,
    BusinessId,
    MCB,
    NominalCurrent,
    ObjectId,
    PoleCount,
    RatedVoltage,
    TripCharacteristic,
    validate_mcb,
)


def make_mcb(**overrides):
    values = {
        "object_id": ObjectId.new(),
        "business_id": BusinessId("MCB-000001"),
        "manufacturer": "Beispiel GmbH",
        "product_name": "LS B16",
        "nominal_current": NominalCurrent(16),
        "rated_voltage": RatedVoltage(230),
        "trip_characteristic": TripCharacteristic.B,
        "pole_count": PoleCount(1),
        "breaking_capacity": BreakingCapacity(6000),
    }
    values.update(overrides)
    return MCB(**values)


def test_valid_mcb_passes_start_profile():
    result = validate_mcb(make_mcb())
    assert result.is_valid
    assert result.messages == ()
    assert tuple(str(rule_id) for rule_id in result.executed_rule_ids) == (
        "REQ-MCB-0001",
        "REQ-MCB-0002",
        "REQ-MCB-0003",
        "REQ-MCB-0004",
    )


def test_unsupported_nominal_current_is_reported():
    result = validate_mcb(make_mcb(nominal_current=NominalCurrent(15)))
    assert not result.is_valid
    assert str(result.errors[0].code) == "ERR-MCB-0001"


def test_unsupported_voltage_and_breaking_capacity_are_reported():
    result = validate_mcb(
        make_mcb(
            rated_voltage=RatedVoltage(110),
            breaking_capacity=BreakingCapacity(3000),
        )
    )
    assert {str(message.code) for message in result.errors} == {
        "ERR-MCB-0002",
        "ERR-MCB-0003",
    }


def test_single_pole_high_current_creates_warning_only():
    result = validate_mcb(make_mcb(nominal_current=NominalCurrent(50)))
    assert result.is_valid
    assert str(result.warnings[0].code) == "WARN-MCB-0001"


def test_mcb_requires_mcb_business_id():
    with pytest.raises(ValueError):
        make_mcb(business_id=BusinessId("RCCB-000001"))


def test_value_objects_reject_invalid_values():
    with pytest.raises(ValueError):
        NominalCurrent(0)
    with pytest.raises(ValueError):
        RatedVoltage(0)
    with pytest.raises(ValueError):
        BreakingCapacity(0)
    with pytest.raises(ValueError):
        PoleCount(5)


def test_mcb_is_immutable():
    mcb = make_mcb()
    with pytest.raises(FrozenInstanceError):
        mcb.product_name = "Geändert"
