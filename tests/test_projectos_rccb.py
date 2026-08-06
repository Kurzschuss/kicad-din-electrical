from dataclasses import FrozenInstanceError

import pytest

from projectos import (
    BusinessId,
    ObjectId,
    RCCB,
    RCCBPoleCount,
    RCCBRatedVoltage,
    RCCBType,
    RatedCurrent,
    ResidualCurrent,
    validate_rccb,
)


def make_rccb(**overrides):
    values = {
        "object_id": ObjectId.new(),
        "business_id": BusinessId("RCCB-000001"),
        "manufacturer": "ProjectOS Test",
        "product_name": "RCCB 40 A / 30 mA",
        "rated_current": RatedCurrent(40),
        "residual_current": ResidualCurrent(30),
        "rated_voltage": RCCBRatedVoltage(230),
        "pole_count": RCCBPoleCount(2),
        "rccb_type": RCCBType.A,
    }
    values.update(overrides)
    return RCCB(**values)


def test_valid_rccb_passes_start_profile():
    result = validate_rccb(make_rccb())

    assert result.is_valid
    assert result.messages == ()


def test_unsupported_rated_current_is_rejected():
    result = validate_rccb(make_rccb(rated_current=RatedCurrent(32)))

    assert not result.is_valid
    assert result.errors[0].code == BusinessId("ERR-RCCB-0001")


def test_unsupported_residual_current_is_rejected():
    result = validate_rccb(make_rccb(residual_current=ResidualCurrent(50)))

    assert not result.is_valid
    assert result.errors[0].code == BusinessId("ERR-RCCB-0002")


def test_400_volt_requires_four_poles_in_start_profile():
    result = validate_rccb(
        make_rccb(rated_voltage=RCCBRatedVoltage(400), pole_count=RCCBPoleCount(2))
    )

    assert not result.is_valid
    assert result.errors[0].code == BusinessId("ERR-RCCB-0004")


def test_type_ac_creates_warning_but_stays_valid():
    result = validate_rccb(make_rccb(rccb_type=RCCBType.AC))

    assert result.is_valid
    assert result.warnings[0].code == BusinessId("WARN-RCCB-0001")


def test_business_id_must_use_rccb_prefix():
    with pytest.raises(ValueError):
        make_rccb(business_id=BusinessId("MCB-000001"))


def test_rccb_is_immutable():
    rccb = make_rccb()

    with pytest.raises(FrozenInstanceError):
        rccb.manufacturer = "Geändert"


@pytest.mark.parametrize("value", [0, -1, 1, 3, 5])
def test_invalid_pole_counts_are_rejected(value):
    with pytest.raises(ValueError):
        RCCBPoleCount(value)
