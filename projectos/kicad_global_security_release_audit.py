"""Persistente und auditierbare Freigabeentscheidungen zur globalen Sicherheitsbesetzung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_global_security_quality_gate import GlobalSecurityStaffingGateResult, GlobalSecurityStaffingDecision


@dataclass(frozen=True, slots=True)
class GlobalSecurityStaffingReleaseRecord:
    release_id: BusinessId
    decided_at: datetime
    decision: GlobalSecurityStaffingDecision
    actor_id: BusinessId
    acting_role: BusinessId
    reason: str
    correlation_id: CorrelationId
    primary_user_id: BusinessId | None
    deputy_user_id: BusinessId | None
    primary_active: bool
    deputy_active: bool
    total_changes: int
    latest_change_at: datetime | None
    finding_codes: tuple[str, ...]


class SQLiteGlobalSecurityStaffingReleaseRepository:
    """Nur anhängbare Historie technischer Freigabeentscheidungen zur Besetzung."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projectos_global_security_staffing_release_audit (
                release_id TEXT PRIMARY KEY,
                decided_at TEXT NOT NULL,
                decision TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                acting_role TEXT NOT NULL,
                reason TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                primary_user_id TEXT,
                deputy_user_id TEXT,
                primary_active INTEGER NOT NULL,
                deputy_active INTEGER NOT NULL,
                total_changes INTEGER NOT NULL,
                latest_change_at TEXT,
                finding_codes_json TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_global_security_staffing_release_time "
            "ON projectos_global_security_staffing_release_audit(decided_at DESC, release_id DESC)"
        )
        self._connection.commit()

    def append(
        self,
        *,
        release_id: BusinessId,
        gate_result: GlobalSecurityStaffingGateResult,
        decided_at: datetime,
        actor_id: BusinessId,
        acting_role: BusinessId,
        reason: str,
        correlation_id: CorrelationId,
    ) -> GlobalSecurityStaffingReleaseRecord:
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0142: Der Freigabezeitpunkt benötigt eine Zeitzone.")
        normalized = reason.strip()
        if not normalized:
            raise ValueError("ERR-KICAD-0143: Die Freigabeentscheidung benötigt eine Begründung.")
        diagnostic = gate_result.diagnostic
        primary_id = diagnostic.primary.user_id if diagnostic.primary else None
        deputy_id = diagnostic.deputy.user_id if diagnostic.deputy else None
        codes = tuple(item.code for item in gate_result.findings)
        try:
            self._connection.execute(
                "INSERT INTO projectos_global_security_staffing_release_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(release_id), decided_at.astimezone(timezone.utc).isoformat(), gate_result.decision.value,
                    str(actor_id), str(acting_role), normalized, str(correlation_id),
                    str(primary_id) if primary_id else None, str(deputy_id) if deputy_id else None,
                    int(diagnostic.primary_active), int(diagnostic.deputy_active), diagnostic.total_changes,
                    diagnostic.latest_change_at.isoformat() if diagnostic.latest_change_at else None,
                    json.dumps(codes, separators=(",", ":")),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0144: Die Freigabeentscheidungskennung ist bereits vorhanden.") from exc
        return self.get(release_id)

    def get(self, release_id: BusinessId) -> GlobalSecurityStaffingReleaseRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_global_security_staffing_release_audit WHERE release_id = ?",
            (str(release_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0145: Die Freigabeentscheidung wurde nicht gefunden.")
        return _decode(row)

    def list_all(self) -> tuple[GlobalSecurityStaffingReleaseRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_global_security_staffing_release_audit ORDER BY decided_at DESC, release_id DESC"
        ).fetchall()
        return tuple(_decode(row) for row in rows)


def _decode(row: tuple[object, ...]) -> GlobalSecurityStaffingReleaseRecord:
    return GlobalSecurityStaffingReleaseRecord(
        release_id=BusinessId(str(row[0])),
        decided_at=datetime.fromisoformat(str(row[1])),
        decision=GlobalSecurityStaffingDecision(str(row[2])),
        actor_id=BusinessId(str(row[3])),
        acting_role=BusinessId(str(row[4])),
        reason=str(row[5]),
        correlation_id=CorrelationId(str(row[6])),
        primary_user_id=BusinessId(str(row[7])) if row[7] else None,
        deputy_user_id=BusinessId(str(row[8])) if row[8] else None,
        primary_active=bool(row[9]),
        deputy_active=bool(row[10]),
        total_changes=int(row[11]),
        latest_change_at=datetime.fromisoformat(str(row[12])) if row[12] else None,
        finding_codes=tuple(json.loads(str(row[13]))),
    )
