from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from projectos.identifiers import BusinessId, CorrelationId, ObjectId


def test_object_id_new_erzeugt_gueltige_eindeutige_uuid() -> None:
    first = ObjectId.new()
    second = ObjectId.new()

    assert isinstance(first.value, UUID)
    assert first != second
    assert str(first) == str(first.value)


def test_object_id_parse_weist_null_uuid_ab() -> None:
    with pytest.raises(ValueError):
        ObjectId.parse("00000000-0000-0000-0000-000000000000")


def test_business_id_normalisiert_und_validiert() -> None:
    identifier = BusinessId.parse(" req-mcb-0007 ")

    assert identifier.value == "REQ-MCB-0007"
    assert str(identifier) == "REQ-MCB-0007"


@pytest.mark.parametrize("value", ["", "MCB 0001", "MCB_0001", "-MCB", "MCB-"])
def test_business_id_weist_ungueltige_werte_ab(value: str) -> None:
    with pytest.raises(ValueError):
        BusinessId.parse(value)


def test_correlation_id_wird_deterministisch_formatiert() -> None:
    identifier = CorrelationId.from_sequence(45)

    assert identifier.value == "COR-00000045"
    assert CorrelationId.parse("cor-00000045") == identifier


@pytest.mark.parametrize("sequence", [0, -1, 100_000_000])
def test_correlation_id_weist_ungueltige_sequenzen_ab(sequence: int) -> None:
    with pytest.raises(ValueError):
        CorrelationId.from_sequence(sequence)


def test_identifier_sind_unveraenderlich() -> None:
    identifier = BusinessId("MCB-000123")

    with pytest.raises(FrozenInstanceError):
        identifier.value = "MCB-000124"  # type: ignore[misc]
