"""Persistente und auditierbare KiCad-Freigabeentscheidungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_quality_gate import KiCadQualityGateResult, KiCadReleaseDecision


@dataclass(frozen=True, slots=True)
class KiCadReleaseAuditRecord:
    release_decision_id: BusinessId
    project_id: BusinessId
    validation_id: BusinessId | None
    decision: KiCadReleaseDecision
    decided_at: datetime
    actor_id: BusinessId
    acting_role: BusinessId
    correlation_id: CorrelationId
    reason: str
    gate_finding_codes: tuple[str, ...]


class SQLiteKiCadReleaseAuditRepository:
    """Nur anhängbare Historie technischer KiCad-Freigabeentscheidungen."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_kicad_release_audit (
                release_decision_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                validation_id TEXT,
                decision TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                acting_role TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                gate_finding_codes_json TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_kicad_release_project_time "
            "ON projectos_kicad_release_audit(project_id, decided_at DESC, release_decision_id DESC)"
        )
        self._connection.commit()

    def append(
        self,
        *,
        release_decision_id: BusinessId,
        gate_result: KiCadQualityGateResult,
        decided_at: datetime,
        actor_id: BusinessId,
        acting_role: BusinessId,
        correlation_id: CorrelationId,
        reason: str,
    ) -> KiCadReleaseAuditRecord:
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0074: Der Entscheidungszeitpunkt benötigt eine Zeitzone.")
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("ERR-KICAD-0075: Eine Freigabeentscheidung benötigt eine Begründung.")
        validation_id = gate_result.latest_validation.validation_id if gate_result.latest_validation else None
        codes = tuple(item.code for item in gate_result.findings)
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_release_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(release_decision_id), str(gate_result.project_id),
                    str(validation_id) if validation_id else None, gate_result.decision.value,
                    decided_at.isoformat(), str(actor_id), str(acting_role), str(correlation_id),
                    normalized_reason,
                    json.dumps(codes, ensure_ascii=False, separators=(",", ":")),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0076: Die Freigabeentscheidungskennung ist bereits vorhanden.") from exc
        return self.get(release_decision_id)

    def get(self, release_decision_id: BusinessId) -> KiCadReleaseAuditRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_kicad_release_audit WHERE release_decision_id = ?",
            (str(release_decision_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0077: Freigabeentscheidung nicht gefunden.")
        return _decode_record(row)

    def list_for_project(self, project_id: BusinessId) -> tuple[KiCadReleaseAuditRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_release_audit WHERE project_id = ? "
            "ORDER BY decided_at DESC, release_decision_id DESC",
            (str(project_id),),
        ).fetchall()
        return tuple(_decode_record(row) for row in rows)


def _decode_record(row: tuple[object, ...]) -> KiCadReleaseAuditRecord:
    return KiCadReleaseAuditRecord(
        release_decision_id=BusinessId(str(row[0])),
        project_id=BusinessId(str(row[1])),
        validation_id=BusinessId(str(row[2])) if row[2] else None,
        decision=KiCadReleaseDecision(str(row[3])),
        decided_at=datetime.fromisoformat(str(row[4])),
        actor_id=BusinessId(str(row[5])),
        acting_role=BusinessId(str(row[6])),
        correlation_id=CorrelationId(str(row[7])),
        reason=str(row[8]),
        gate_finding_codes=tuple(json.loads(str(row[9]))),
    )
