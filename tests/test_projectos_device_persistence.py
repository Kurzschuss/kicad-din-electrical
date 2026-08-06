from dataclasses import replace

from projectos import (
    BreakingCapacity,
    BusinessId,
    MCB,
    NominalCurrent,
    ObjectId,
    PoleCount,
    RCCB,
    RCCBPoleCount,
    RCCBRatedVoltage,
    RCCBType,
    RatedCurrent,
    RatedVoltage,
    ResidualCurrent,
    SQLiteUnitOfWork,
    TripCharacteristic,
    create_mcb_sqlite_repository,
    create_rccb_sqlite_repository,
    decode_mcb,
    decode_rccb,
    encode_mcb,
    encode_rccb,
)


def make_mcb() -> MCB:
    return MCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("MCB-000901"),
        manufacturer="ProjectOS",
        product_name="MCB C16",
        nominal_current=NominalCurrent(16),
        rated_voltage=RatedVoltage(230),
        breaking_capacity=BreakingCapacity(6000),
        pole_count=PoleCount(1),
        trip_characteristic=TripCharacteristic.C,
    )


def make_rccb() -> RCCB:
    return RCCB(
        object_id=ObjectId.new(),
        business_id=BusinessId("RCCB-000901"),
        manufacturer="ProjectOS",
        product_name="RCCB A 40/0.03",
        rated_current=RatedCurrent(40),
        residual_current=ResidualCurrent(30),
        rated_voltage=RCCBRatedVoltage(230),
        pole_count=RCCBPoleCount(2),
        rccb_type=RCCBType.A,
    )


def test_mcb_codec_roundtrip() -> None:
    mcb = make_mcb()
    assert decode_mcb(encode_mcb(mcb)) == mcb


def test_rccb_codec_roundtrip() -> None:
    rccb = make_rccb()
    assert decode_rccb(encode_rccb(rccb)) == rccb


def test_mcb_und_rccb_werden_getrennt_persistiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()
    rccb = make_rccb()

    with SQLiteUnitOfWork(database) as uow:
        assert uow.connection is not None
        mcb_repository = create_mcb_sqlite_repository(uow.connection)
        rccb_repository = create_rccb_sqlite_repository(uow.connection)
        assert mcb_repository.add(mcb).is_success
        assert rccb_repository.add(rccb).is_success

    with SQLiteUnitOfWork(database) as uow:
        assert uow.connection is not None
        loaded_mcb = create_mcb_sqlite_repository(uow.connection).get(mcb.object_id)
        loaded_rccb = create_rccb_sqlite_repository(uow.connection).get(rccb.object_id)
        assert loaded_mcb is not None and loaded_mcb.entity == mcb
        assert loaded_rccb is not None and loaded_rccb.entity == rccb
        assert loaded_mcb.revision == 1
        assert loaded_rccb.revision == 1


def test_mcb_revision_wird_beim_speichern_erhoeht(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()

    with SQLiteUnitOfWork(database) as uow:
        assert uow.connection is not None
        repository = create_mcb_sqlite_repository(uow.connection)
        assert repository.add(mcb).is_success
        updated = replace(mcb, product_name="MCB C16 aktualisiert")
        result = repository.save(updated, expected_revision=1)
        assert result.is_success
        assert result.value is not None
        assert result.value.revision == 2

    with SQLiteUnitOfWork(database) as uow:
        assert uow.connection is not None
        record = create_mcb_sqlite_repository(uow.connection).get(mcb.object_id)
        assert record is not None
        assert record.entity.product_name == "MCB C16 aktualisiert"
        assert record.revision == 2
