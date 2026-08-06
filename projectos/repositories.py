"""Repository-Verträge und eine deterministische In-Memory-Referenzimplementierung."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from .identifiers import BusinessId, ObjectId
from .results import MessageSeverity, Result, ResultMessage

T = TypeVar("T")


class RepositoryEntity(Protocol):
    """Minimaler Vertrag für speicherbare ProjectOS-Entitäten."""

    object_id: ObjectId
    business_id: BusinessId


@dataclass(frozen=True, slots=True)
class RepositoryRecord(Generic[T]):
    """Gespeicherte Entität mit technischer Revisionsnummer."""

    entity: T
    revision: int

    def __post_init__(self) -> None:
        if self.revision < 1:
            raise ValueError("Eine Repository-Revision muss mindestens 1 sein.")


class Repository(Generic[T], Protocol):
    """Technologieunabhängiger Repository-Vertrag."""

    def get(self, object_id: ObjectId) -> RepositoryRecord[T] | None: ...

    def get_by_business_id(self, business_id: BusinessId) -> RepositoryRecord[T] | None: ...

    def add(self, entity: T) -> Result[RepositoryRecord[T]]: ...

    def save(self, entity: T, *, expected_revision: int) -> Result[RepositoryRecord[T]]: ...

    def delete(self, object_id: ObjectId, *, expected_revision: int) -> Result[None]: ...

    def list_all(self) -> tuple[RepositoryRecord[T], ...]: ...


class InMemoryRepository(Generic[T]):
    """Deterministische Referenzimplementierung für Tests und Simulationen."""

    def __init__(self) -> None:
        self._records: dict[ObjectId, RepositoryRecord[T]] = {}
        self._business_index: dict[BusinessId, ObjectId] = {}

    def get(self, object_id: ObjectId) -> RepositoryRecord[T] | None:
        return self._records.get(object_id)

    def get_by_business_id(self, business_id: BusinessId) -> RepositoryRecord[T] | None:
        object_id = self._business_index.get(business_id)
        return None if object_id is None else self._records[object_id]

    def add(self, entity: T) -> Result[RepositoryRecord[T]]:
        object_id, business_id = self._identity(entity)
        if object_id in self._records:
            return self._failure("ERR-REP-0001", "Die technische Objektkennung ist bereits vorhanden.")
        if business_id in self._business_index:
            return self._failure("ERR-REP-0002", "Die fachliche Kennung ist bereits vorhanden.")

        record = RepositoryRecord(entity=entity, revision=1)
        self._records[object_id] = record
        self._business_index[business_id] = object_id
        return Result.success(record)

    def save(self, entity: T, *, expected_revision: int) -> Result[RepositoryRecord[T]]:
        object_id, business_id = self._identity(entity)
        current = self._records.get(object_id)
        if current is None:
            return self._failure("ERR-REP-0003", "Das zu speichernde Objekt wurde nicht gefunden.")
        if expected_revision != current.revision:
            return self._failure("ERR-REP-0004", "Die erwartete Revision stimmt nicht mit dem gespeicherten Stand überein.")

        indexed_object_id = self._business_index.get(business_id)
        if indexed_object_id not in {None, object_id}:
            return self._failure("ERR-REP-0002", "Die fachliche Kennung ist bereits vorhanden.")

        previous_business_id = current.entity.business_id  # type: ignore[attr-defined]
        if previous_business_id != business_id:
            del self._business_index[previous_business_id]
            self._business_index[business_id] = object_id

        updated = RepositoryRecord(entity=entity, revision=current.revision + 1)
        self._records[object_id] = updated
        return Result.success(updated)

    def delete(self, object_id: ObjectId, *, expected_revision: int) -> Result[None]:
        current = self._records.get(object_id)
        if current is None:
            return self._failure("ERR-REP-0003", "Das zu löschende Objekt wurde nicht gefunden.")
        if expected_revision != current.revision:
            return self._failure("ERR-REP-0004", "Die erwartete Revision stimmt nicht mit dem gespeicherten Stand überein.")

        business_id = current.entity.business_id  # type: ignore[attr-defined]
        del self._records[object_id]
        del self._business_index[business_id]
        return Result.success(None)

    def list_all(self) -> tuple[RepositoryRecord[T], ...]:
        return tuple(self._records.values())

    @staticmethod
    def _identity(entity: T) -> tuple[ObjectId, BusinessId]:
        object_id = getattr(entity, "object_id", None)
        business_id = getattr(entity, "business_id", None)
        if not isinstance(object_id, ObjectId) or not isinstance(business_id, BusinessId):
            raise TypeError("Repository-Entitäten benötigen ObjectId und BusinessId.")
        return object_id, business_id

    @staticmethod
    def _failure(code: str, text: str) -> Result[RepositoryRecord[T]]:
        return Result.failure(
            ResultMessage(
                code=BusinessId.parse(code),
                severity=MessageSeverity.ERROR,
                text=text,
            )
        )
