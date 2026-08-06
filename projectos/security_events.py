"""Kanonisches Sicherheitsereignismodell zur Ablösung rekursiver Alarmketten."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import json
import sqlite3

from .identifiers import BusinessId, CorrelationId


class SecurityEventSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SecurityEventStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class SecurityEventKind(StrEnum):
    RELEASE_ATTEMPT_DENIED = "RELEASE_ATTEMPT_DENIED"
    ALERT_ACTION_DENIED = "ALERT_ACTION_DENIED"
    RESPONSIBILITY_UNAVAILABLE = "RESPONSIBILITY_UNAVAILABLE"
    THRESHOLD_EXCEEDED = "THRESHOLD_EXCEEDED"


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    event_id: BusinessId
    kind: SecurityEventKind
    severity: SecurityEventSeverity
    status: SecurityEventStatus
    occurred_at: datetime
    source_type: str
    source_id: BusinessId
    correlation_id: CorrelationId
    code: str
    message: str
    actor_id: BusinessId | None = None
    parent_event_id: BusinessId | None = None
    metadata: dict[str, str] | None = None


class SQLiteSecurityEventRepository:
    """Append-only Ereignisse; Statusänderungen bleiben explizit und nachvollziehbar."""

    TABLE = "projectos_security_events"

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        connection.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
                event_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                actor_id TEXT,
                parent_event_id TEXT,
                correlation_id TEXT NOT NULL,
                code TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            )"""
        )
        connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_security_events_source ON {self.TABLE}(source_type, source_id, occurred_at DESC)"
        )
        connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_security_events_status ON {self.TABLE}(status, severity, occurred_at DESC)"
        )
        connection.commit()

    def append(self, event: SecurityEvent) -> SecurityEvent:
        if event.occurred_at.tzinfo is None or event.occurred_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0337: Sicherheitsereignis benötigt eine Zeitzone.")
        code = event.code.strip().upper()
        message = event.message.strip()
        source_type = event.source_type.strip().upper()
        if not code or not message or not source_type:
            raise ValueError("ERR-KICAD-0338: Code, Meldung und Quelltyp sind erforderlich.")
        try:
            self._connection.execute(
                f"INSERT INTO {self.TABLE} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    str(event.event_id), event.kind.value, event.severity.value, event.status.value,
                    event.occurred_at.astimezone(timezone.utc).isoformat(), source_type,
                    str(event.source_id), str(event.actor_id) if event.actor_id else None,
                    str(event.parent_event_id) if event.parent_event_id else None,
                    str(event.correlation_id), code, message,
                    json.dumps(event.metadata or {}, sort_keys=True, separators=(",", ":")),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0339: Sicherheitsereigniskennung ist bereits vorhanden.") from exc
        return self.get(event.event_id)

    def get(self, event_id: BusinessId) -> SecurityEvent:
        row = self._connection.execute(
            f"SELECT * FROM {self.TABLE} WHERE event_id=?", (str(event_id),)
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0340: Sicherheitsereignis wurde nicht gefunden.")
        return self._decode(row)

    def list_for_source(self, source_type: str, source_id: BusinessId) -> tuple[SecurityEvent, ...]:
        rows = self._connection.execute(
            f"SELECT * FROM {self.TABLE} WHERE source_type=? AND source_id=? ORDER BY occurred_at,event_id",
            (source_type.strip().upper(), str(source_id)),
        ).fetchall()
        return tuple(self._decode(row) for row in rows)

    @staticmethod
    def _decode(row: tuple[object, ...]) -> SecurityEvent:
        return SecurityEvent(
            event_id=BusinessId(str(row[0])), kind=SecurityEventKind(str(row[1])),
            severity=SecurityEventSeverity(str(row[2])), status=SecurityEventStatus(str(row[3])),
            occurred_at=datetime.fromisoformat(str(row[4])), source_type=str(row[5]),
            source_id=BusinessId(str(row[6])), actor_id=BusinessId(str(row[7])) if row[7] else None,
            parent_event_id=BusinessId(str(row[8])) if row[8] else None,
            correlation_id=CorrelationId(str(row[9])), code=str(row[10]), message=str(row[11]),
            metadata=dict(json.loads(str(row[12]))),
        )
