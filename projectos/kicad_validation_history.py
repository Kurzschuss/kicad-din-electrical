"""Persistente Historie und Vergleich projektweiter KiCad-Validierungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3

from .identifiers import BusinessId, CorrelationId
from .kicad_library_validation import KiCadValidationFinding, KiCadValidationSeverity
from .kicad_project_validation import KiCadProjectValidationResult


@dataclass(frozen=True, slots=True)
class KiCadValidationHistoryRecord:
    validation_id: BusinessId
    project_id: BusinessId
    recorded_at: datetime
    correlation_id: CorrelationId
    valid: bool
    target_count: int
    exception_count: int
    findings: tuple[KiCadValidationFinding, ...]
    fingerprint: str


@dataclass(frozen=True, slots=True)
class KiCadValidationComparison:
    older_validation_id: BusinessId
    newer_validation_id: BusinessId
    added_findings: tuple[KiCadValidationFinding, ...]
    removed_findings: tuple[KiCadValidationFinding, ...]
    validity_changed: bool
    exception_delta: int


class SQLiteKiCadValidationHistoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projectos_kicad_validation_history (
                validation_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                valid INTEGER NOT NULL,
                target_count INTEGER NOT NULL,
                exception_count INTEGER NOT NULL,
                findings_json TEXT NOT NULL,
                fingerprint TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_kicad_validation_project_time "
            "ON projectos_kicad_validation_history(project_id, recorded_at DESC, validation_id DESC)"
        )
        self._connection.commit()

    def append(
        self,
        *,
        validation_id: BusinessId,
        project_id: BusinessId,
        recorded_at: datetime,
        correlation_id: CorrelationId,
        result: KiCadProjectValidationResult,
    ) -> KiCadValidationHistoryRecord:
        if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
            raise ValueError("ERR-KICAD-0055: Der Validierungszeitpunkt benötigt eine Zeitzone.")
        findings_json = _encode_findings(result.findings)
        fingerprint = _fingerprint(result, findings_json)
        try:
            self._connection.execute(
                "INSERT INTO projectos_kicad_validation_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(validation_id), str(project_id), recorded_at.isoformat(), str(correlation_id),
                    int(result.valid), result.target_count, result.exception_count,
                    findings_json, fingerprint,
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("ERR-KICAD-0056: Die Validierungskennung ist bereits vorhanden.") from exc
        return self.get(validation_id)

    def get(self, validation_id: BusinessId) -> KiCadValidationHistoryRecord:
        row = self._connection.execute(
            "SELECT * FROM projectos_kicad_validation_history WHERE validation_id = ?",
            (str(validation_id),),
        ).fetchone()
        if row is None:
            raise ValueError("ERR-KICAD-0057: Validierungshistorieneintrag nicht gefunden.")
        return _decode_record(row)

    def list_for_project(self, project_id: BusinessId) -> tuple[KiCadValidationHistoryRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM projectos_kicad_validation_history WHERE project_id = ? "
            "ORDER BY recorded_at DESC, validation_id DESC",
            (str(project_id),),
        ).fetchall()
        return tuple(_decode_record(row) for row in rows)

    def compare(
        self,
        older_validation_id: BusinessId,
        newer_validation_id: BusinessId,
    ) -> KiCadValidationComparison:
        older = self.get(older_validation_id)
        newer = self.get(newer_validation_id)
        if older.project_id != newer.project_id:
            raise ValueError("ERR-KICAD-0058: Validierungen unterschiedlicher Projekte sind nicht vergleichbar.")
        older_map = {_finding_key(item): item for item in older.findings}
        newer_map = {_finding_key(item): item for item in newer.findings}
        added = tuple(newer_map[key] for key in sorted(newer_map.keys() - older_map.keys()))
        removed = tuple(older_map[key] for key in sorted(older_map.keys() - newer_map.keys()))
        return KiCadValidationComparison(
            older.validation_id,
            newer.validation_id,
            added,
            removed,
            older.valid != newer.valid,
            newer.exception_count - older.exception_count,
        )


def _finding_key(item: KiCadValidationFinding) -> tuple[str, str, str, str]:
    return (item.code, item.severity.value, str(item.asset_id or ""), item.message)


def _encode_findings(findings: tuple[KiCadValidationFinding, ...]) -> str:
    payload = [
        {"code": item.code, "severity": item.severity.value, "message": item.message,
         "asset_id": str(item.asset_id) if item.asset_id else None}
        for item in findings
    ]
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _decode_record(row: tuple[object, ...]) -> KiCadValidationHistoryRecord:
    payload = json.loads(str(row[7]))
    findings = tuple(
        KiCadValidationFinding(
            item["code"], KiCadValidationSeverity(item["severity"]), item["message"],
            BusinessId(item["asset_id"]) if item["asset_id"] else None,
        )
        for item in payload
    )
    return KiCadValidationHistoryRecord(
        BusinessId(str(row[0])), BusinessId(str(row[1])), datetime.fromisoformat(str(row[2])),
        CorrelationId(str(row[3])), bool(row[4]), int(row[5]), int(row[6]), findings, str(row[8]),
    )


def _fingerprint(result: KiCadProjectValidationResult, findings_json: str) -> str:
    canonical = json.dumps(
        {"valid": result.valid, "target_count": result.target_count,
         "exception_count": result.exception_count, "findings": json.loads(findings_json)},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()
