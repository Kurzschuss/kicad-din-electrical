"""SQLite-Persistenzadapter und transaktionale Unit of Work für ProjectOS."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Generic, TypeVar

from .identifiers import BusinessId, ObjectId
from .repositories import RepositoryRecord
from .results import MessageSeverity, Result, ResultMessage

T = TypeVar("T")

Encoder = Callable[[T], Mapping[str, object]]
Decoder = Callable[[Mapping[str, object]], T]


class SQLiteUnitOfWork(AbstractContextManager["SQLiteUnitOfWork"]):
    """Explizite SQLite-Transaktionsgrenze mit Commit und Rollback."""

    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        self.connection: sqlite3.Connection | None = None

    def __enter__(self) -> "SQLiteUnitOfWork":
        if self.connection is not None:
            raise RuntimeError("Die Unit of Work ist bereits geöffnet.")
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("BEGIN IMMEDIATE")
        return self

    def commit(self) -> None:
        if self.connection is None:
            raise RuntimeError("Die Unit of Work ist nicht geöffnet.")
        self.connection.commit()

    def rollback(self) -> None:
        if self.connection is None:
            raise RuntimeError("Die Unit of Work ist nicht geöffnet.")
        self.connection.rollback()

    def __exit__(self, exc_type, exc, traceback) -> bool:
        assert self.connection is not None
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.connection.close()
            self.connection = None
        return False


@dataclass(frozen=True, slots=True)
class SQLiteRepositoryConfig:
    """Konfiguration eines typisierten SQLite-JSON-Repositories."""

    entity_type: str

    def __post_init__(self) -> None:
        normalized = self.entity_type.strip().lower()
        if not normalized or not normalized.replace("_", "").isalnum():
            raise ValueError("entity_type darf nur Buchstaben, Ziffern und Unterstriche enthalten.")
        object.__setattr__(self, "entity_type", normalized)


class SQLiteJsonRepository(Generic[T]):
    """SQLite-Repository mit explizitem JSON-Codec und Revisionskontrolle."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        config: SQLiteRepositoryConfig,
        encode: Encoder[T],
        decode: Decoder[T],
    ) -> None:
        self._connection = connection
        self._config = config
        self._encode = encode
        self._decode = decode
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_entities (
                entity_type TEXT NOT NULL,
                object_id TEXT NOT NULL,
                business_id TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision >= 1),
                payload TEXT NOT NULL,
                PRIMARY KEY (entity_type, object_id),
                UNIQUE (entity_type, business_id)
            )
            """
        )

    def get(self, object_id: ObjectId) -> RepositoryRecord[T] | None:
        row = self._connection.execute(
            "SELECT payload, revision FROM projectos_entities WHERE entity_type = ? AND object_id = ?",
            (self._config.entity_type, str(object_id)),
        ).fetchone()
        return None if row is None else self._record(row)

    def get_by_business_id(self, business_id: BusinessId) -> RepositoryRecord[T] | None:
        row = self._connection.execute(
            "SELECT payload, revision FROM projectos_entities WHERE entity_type = ? AND business_id = ?",
            (self._config.entity_type, str(business_id)),
        ).fetchone()
        return None if row is None else self._record(row)

    def add(self, entity: T) -> Result[RepositoryRecord[T]]:
        object_id, business_id = self._identity(entity)
        payload = self._serialize(entity)
        try:
            self._connection.execute(
                "INSERT INTO projectos_entities(entity_type, object_id, business_id, revision, payload) VALUES (?, ?, ?, 1, ?)",
                (self._config.entity_type, str(object_id), str(business_id), payload),
            )
        except sqlite3.IntegrityError:
            if self.get(object_id) is not None:
                return self._failure("ERR-REP-0001", "Die technische Objektkennung ist bereits vorhanden.")
            return self._failure("ERR-REP-0002", "Die fachliche Kennung ist bereits vorhanden.")
        return Result.success(RepositoryRecord(entity, 1))

    def save(self, entity: T, *, expected_revision: int) -> Result[RepositoryRecord[T]]:
        object_id, business_id = self._identity(entity)
        new_revision = expected_revision + 1
        try:
            cursor = self._connection.execute(
                """
                UPDATE projectos_entities
                   SET business_id = ?, revision = ?, payload = ?
                 WHERE entity_type = ? AND object_id = ? AND revision = ?
                """,
                (
                    str(business_id),
                    new_revision,
                    self._serialize(entity),
                    self._config.entity_type,
                    str(object_id),
                    expected_revision,
                ),
            )
        except sqlite3.IntegrityError:
            return self._failure("ERR-REP-0002", "Die fachliche Kennung ist bereits vorhanden.")
        if cursor.rowcount == 0:
            if self.get(object_id) is None:
                return self._failure("ERR-REP-0003", "Das zu speichernde Objekt wurde nicht gefunden.")
            return self._failure("ERR-REP-0004", "Die erwartete Revision stimmt nicht mit dem gespeicherten Stand überein.")
        return Result.success(RepositoryRecord(entity, new_revision))

    def delete(self, object_id: ObjectId, *, expected_revision: int) -> Result[None]:
        cursor = self._connection.execute(
            "DELETE FROM projectos_entities WHERE entity_type = ? AND object_id = ? AND revision = ?",
            (self._config.entity_type, str(object_id), expected_revision),
        )
        if cursor.rowcount == 0:
            if self.get(object_id) is None:
                return Result.failure(self._message("ERR-REP-0003", "Das zu löschende Objekt wurde nicht gefunden."))
            return Result.failure(self._message("ERR-REP-0004", "Die erwartete Revision stimmt nicht mit dem gespeicherten Stand überein."))
        return Result.success(None)

    def list_all(self) -> tuple[RepositoryRecord[T], ...]:
        rows = self._connection.execute(
            "SELECT payload, revision FROM projectos_entities WHERE entity_type = ? ORDER BY rowid",
            (self._config.entity_type,),
        ).fetchall()
        return tuple(self._record(row) for row in rows)

    def _record(self, row: sqlite3.Row) -> RepositoryRecord[T]:
        raw = json.loads(row["payload"])
        if not isinstance(raw, dict):
            raise ValueError("Gespeicherte Repository-Nutzdaten müssen ein JSON-Objekt sein.")
        return RepositoryRecord(self._decode(raw), int(row["revision"]))

    def _serialize(self, entity: T) -> str:
        return json.dumps(dict(self._encode(entity)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _identity(entity: T) -> tuple[ObjectId, BusinessId]:
        object_id = getattr(entity, "object_id", None)
        business_id = getattr(entity, "business_id", None)
        if not isinstance(object_id, ObjectId) or not isinstance(business_id, BusinessId):
            raise TypeError("Repository-Entitäten benötigen ObjectId und BusinessId.")
        return object_id, business_id

    @classmethod
    def _failure(cls, code: str, text: str) -> Result[RepositoryRecord[T]]:
        return Result.failure(cls._message(code, text))

    @staticmethod
    def _message(code: str, text: str) -> ResultMessage:
        return ResultMessage(BusinessId(code), MessageSeverity.ERROR, text)
