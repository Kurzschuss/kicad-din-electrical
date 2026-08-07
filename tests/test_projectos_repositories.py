from dataclasses import dataclass

from projectos import BusinessId, InMemoryRepository, ObjectId


@dataclass(frozen=True, slots=True)
class ExampleEntity:
    object_id: ObjectId
    business_id: BusinessId
    name: str


def make_entity(identifier: str = "MCB-000001", name: str = "Beispiel") -> ExampleEntity:
    return ExampleEntity(ObjectId.new(), BusinessId.parse(identifier), name)


def test_add_and_lookup_by_both_identifiers() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    entity = make_entity()

    result = repository.add(entity)

    assert result.is_success
    assert result.value is not None
    assert result.value.revision == 1
    assert repository.get(entity.object_id) == result.value
    assert repository.get_by_business_id(entity.business_id) == result.value


def test_duplicate_object_id_is_rejected() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    entity = make_entity()
    repository.add(entity)

    result = repository.add(ExampleEntity(entity.object_id, BusinessId.parse("MCB-000002"), "Zwei"))

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-REP-0001"


def test_duplicate_business_id_is_rejected() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    first = make_entity()
    repository.add(first)

    result = repository.add(ExampleEntity(ObjectId.new(), first.business_id, "Zwei"))

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-REP-0002"


def test_save_increments_revision() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    entity = make_entity()
    repository.add(entity)
    changed = ExampleEntity(entity.object_id, entity.business_id, "Geändert")

    result = repository.save(changed, expected_revision=1)

    assert result.is_success
    assert result.value is not None
    assert result.value.revision == 2
    assert result.value.entity.name == "Geändert"


def test_stale_revision_is_rejected() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    entity = make_entity()
    repository.add(entity)

    result = repository.save(entity, expected_revision=2)

    assert not result.is_success
    assert str(result.errors[0].code) == "ERR-REP-0004"


def test_delete_checks_revision_and_removes_indexes() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    entity = make_entity()
    repository.add(entity)

    result = repository.delete(entity.object_id, expected_revision=1)

    assert result.is_success
    assert repository.get(entity.object_id) is None
    assert repository.get_by_business_id(entity.business_id) is None


def test_list_all_preserves_insertion_order() -> None:
    repository: InMemoryRepository[ExampleEntity] = InMemoryRepository()
    first = make_entity("MCB-000001")
    second = make_entity("MCB-000002")
    repository.add(first)
    repository.add(second)

    assert tuple(record.entity for record in repository.list_all()) == (first, second)
