from dataclasses import dataclass, replace

import pytest

from projectos import BusinessId, ObjectId, SQLiteJsonRepository, SQLiteRepositoryConfig, SQLiteUnitOfWork


@dataclass(frozen=True, slots=True)
class Device:
    object_id: ObjectId
    business_id: BusinessId
    name: str


def encode(device: Device):
    return {"object_id": str(device.object_id), "business_id": str(device.business_id), "name": device.name}


def decode(data):
    return Device(ObjectId.parse(str(data["object_id"])), BusinessId(str(data["business_id"])), str(data["name"]))


def repository(uow):
    assert uow.connection is not None
    return SQLiteJsonRepository(uow.connection, config=SQLiteRepositoryConfig("device"), encode=encode, decode=decode)


def test_commit_speichert_daten(tmp_path):
    database = tmp_path / "projectos.db"
    device = Device(ObjectId.new(), BusinessId("DEV-0001"), "MCB")
    with SQLiteUnitOfWork(database) as uow:
        result = repository(uow).add(device)
        assert result.is_success
        assert result.value.revision == 1
    with SQLiteUnitOfWork(database) as uow:
        record = repository(uow).get(device.object_id)
        assert record is not None
        assert record.entity == device


def test_exception_rollt_transaktion_zurueck(tmp_path):
    database = tmp_path / "projectos.db"
    device = Device(ObjectId.new(), BusinessId("DEV-0002"), "RCCB")
    with pytest.raises(RuntimeError):
        with SQLiteUnitOfWork(database) as uow:
            repository(uow).add(device)
            raise RuntimeError("Abbruch")
    with SQLiteUnitOfWork(database) as uow:
        assert repository(uow).get(device.object_id) is None


def test_revision_wird_optimistisch_geprueft(tmp_path):
    database = tmp_path / "projectos.db"
    device = Device(ObjectId.new(), BusinessId("DEV-0003"), "Alt")
    with SQLiteUnitOfWork(database) as uow:
        repo = repository(uow)
        repo.add(device)
        updated = repo.save(replace(device, name="Neu"), expected_revision=1)
        assert updated.is_success and updated.value.revision == 2
        conflict = repo.save(replace(device, name="Konflikt"), expected_revision=1)
        assert not conflict.is_success
        assert str(conflict.errors[0].code) == "ERR-REP-0004"


def test_fachliche_kennung_ist_je_typ_eindeutig(tmp_path):
    database = tmp_path / "projectos.db"
    first = Device(ObjectId.new(), BusinessId("DEV-0004"), "A")
    second = Device(ObjectId.new(), BusinessId("DEV-0004"), "B")
    with SQLiteUnitOfWork(database) as uow:
        repo = repository(uow)
        assert repo.add(first).is_success
        duplicate = repo.add(second)
        assert not duplicate.is_success
        assert str(duplicate.errors[0].code) == "ERR-REP-0002"
