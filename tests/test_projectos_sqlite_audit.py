from datetime import datetime, timezone

import pytest

from projectos import (
    AuditEntry, BusinessId, CorrelationId, MCB, NominalCurrent, ObjectId,
    PoleCount, RatedVoltage, TripCharacteristic, BreakingCapacity,
    SQLiteAuditRepository, SQLiteUnitOfWork, add_with_audit,
    create_mcb_sqlite_repository,
)


def make_mcb() -> MCB:
    return MCB(
        ObjectId.new(), BusinessId("MCB-AUD-0001"), "Test", "B16",
        NominalCurrent(16), RatedVoltage(230), BreakingCapacity(6000),
        PoleCount(1), TripCharacteristic.B,
    )


def make_audit(mcb: MCB, previous_hash: str, audit_id: str = "AUD-0001") -> AuditEntry:
    return AuditEntry(
        audit_id=BusinessId(audit_id), occurred_at=datetime(2026, 8, 6, tzinfo=timezone.utc),
        actor_id=BusinessId("USR-0001"), acting_role=BusinessId("ROLE-ENGINEER"),
        permission_id=BusinessId("PERM-MCB-CREATE"), object_id=mcb.object_id,
        object_business_id=mcb.business_id, action="mcb_created", reason="Test",
        correlation_id=CorrelationId.from_sequence(1), new_values={"device": str(mcb.business_id)},
        previous_hash=previous_hash,
    )


def test_geraet_und_audit_werden_atomar_persistiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()
    with SQLiteUnitOfWork(database) as uow:
        repository = create_mcb_sqlite_repository(uow.connection)
        audits = SQLiteAuditRepository(uow.connection)
        result = add_with_audit(repository, audits, mcb, lambda previous: make_audit(mcb, previous))
        assert result.is_success

    with SQLiteUnitOfWork(database) as uow:
        repository = create_mcb_sqlite_repository(uow.connection)
        audits = SQLiteAuditRepository(uow.connection)
        assert repository.get(mcb.object_id) is not None
        assert len(audits.by_object(mcb.object_id)) == 1
        assert audits.verify_integrity()


def test_fehler_nach_geraetespeicherung_rollt_gesamte_transaktion_zurueck(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    mcb = make_mcb()
    with pytest.raises(ValueError):
        with SQLiteUnitOfWork(database) as uow:
            repository = create_mcb_sqlite_repository(uow.connection)
            audits = SQLiteAuditRepository(uow.connection)
            add_with_audit(repository, audits, mcb, lambda _: make_audit(mcb, "falscher-hash"))

    with SQLiteUnitOfWork(database) as uow:
        assert create_mcb_sqlite_repository(uow.connection).get(mcb.object_id) is None
        assert SQLiteAuditRepository(uow.connection).all() == ()


def test_audit_kette_bleibt_nach_mehreren_eintraegen_gueltig(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    first = make_mcb()
    second = MCB(
        ObjectId.new(), BusinessId("MCB-AUD-0002"), "Test", "C16",
        NominalCurrent(16), RatedVoltage(230), BreakingCapacity(6000),
        PoleCount(1), TripCharacteristic.C,
    )
    with SQLiteUnitOfWork(database) as uow:
        repository = create_mcb_sqlite_repository(uow.connection)
        audits = SQLiteAuditRepository(uow.connection)
        add_with_audit(repository, audits, first, lambda previous: make_audit(first, previous, "AUD-0001"))
        add_with_audit(repository, audits, second, lambda previous: make_audit(second, previous, "AUD-0002"))
        assert audits.verify_integrity()
        assert audits.all()[1].previous_hash == audits.all()[0].entry_hash
