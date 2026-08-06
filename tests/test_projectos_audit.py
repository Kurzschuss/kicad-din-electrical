from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from projectos.audit import AuditEntry, InMemoryAuditRepository
from projectos.identifiers import BusinessId, CorrelationId, ObjectId


def make_entry(number: int, *, previous_hash: str = "", object_id: ObjectId | None = None) -> AuditEntry:
    return AuditEntry(
        audit_id=BusinessId(f"AUD-MCB-{number:06d}"),
        occurred_at=datetime(2026, 8, 6, 8, number, tzinfo=timezone.utc),
        actor_id=BusinessId("USR-000042"),
        acting_role=BusinessId("ROLE-PROJEKTLEITER"),
        permission_id=BusinessId("PERM-MCB-EDIT"),
        object_id=object_id or ObjectId.new(),
        object_business_id=BusinessId("MCB-000123"),
        action="nominal_current_changed",
        reason="Technische Korrektur",
        correlation_id=CorrelationId.from_sequence(number),
        previous_values={"nominal_current": 10},
        new_values={"nominal_current": 16},
        previous_hash=previous_hash,
    )


def test_audit_entry_is_immutable_and_hashes_values() -> None:
    entry = make_entry(1)
    assert len(entry.entry_hash) == 64
    with pytest.raises(TypeError):
        entry.new_values["nominal_current"] = 20
    with pytest.raises(FrozenInstanceError):
        entry.reason = "Geändert"


def test_repository_builds_and_verifies_chain() -> None:
    repository = InMemoryAuditRepository()
    first = repository.append(make_entry(1))
    second = repository.append(make_entry(2, previous_hash=first.entry_hash))
    assert repository.all() == (first, second)
    assert repository.verify_integrity()


def test_repository_rejects_wrong_previous_hash() -> None:
    repository = InMemoryAuditRepository()
    repository.append(make_entry(1))
    with pytest.raises(ValueError, match="ERR-AUD-0002"):
        repository.append(make_entry(2, previous_hash="ungueltig"))


def test_repository_rejects_duplicate_audit_id() -> None:
    repository = InMemoryAuditRepository()
    first = repository.append(make_entry(1))
    duplicate = make_entry(1, previous_hash=first.entry_hash)
    with pytest.raises(ValueError, match="ERR-AUD-0001"):
        repository.append(duplicate)


def test_filter_by_object() -> None:
    repository = InMemoryAuditRepository()
    object_id = ObjectId.new()
    first = repository.append(make_entry(1, object_id=object_id))
    repository.append(make_entry(2, previous_hash=first.entry_hash))
    assert repository.by_object(object_id) == (first,)


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="Zeitzonenbezug"):
        AuditEntry(
            audit_id=BusinessId("AUD-MCB-000001"),
            occurred_at=datetime(2026, 8, 6),
            actor_id=BusinessId("USR-000042"),
            acting_role=BusinessId("ROLE-PROJEKTLEITER"),
            permission_id=BusinessId("PERM-MCB-EDIT"),
            object_id=ObjectId.new(),
            object_business_id=BusinessId("MCB-000123"),
            action="changed",
            reason="Grund",
            correlation_id=CorrelationId.from_sequence(1),
        )
