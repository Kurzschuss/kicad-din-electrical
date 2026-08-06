from datetime import datetime, timezone
import sqlite3

import pytest

from projectos import (
    BusinessId, CorrelationId, KiCadQualityGateFinding, KiCadQualityGateResult,
    KiCadReleaseDecision, SQLiteKiCadReleaseAuditRepository,
)


def gate(decision: KiCadReleaseDecision = KiCadReleaseDecision.APPROVED) -> KiCadQualityGateResult:
    findings = () if decision is KiCadReleaseDecision.APPROVED else (
        KiCadQualityGateFinding("ERR-KICAD-0068", "Jüngster Lauf ungültig."),
    )
    return KiCadQualityGateResult(
        BusinessId("PRJ-0001"), decision, 2, None, 0.5, 1, 0, 0, findings,
    )


def repo() -> SQLiteKiCadReleaseAuditRepository:
    return SQLiteKiCadReleaseAuditRepository(sqlite3.connect(":memory:"))


def test_speichert_freigabeentscheidung_mit_verantwortung() -> None:
    record = repo().append(
        release_decision_id=BusinessId("REL-0001"), gate_result=gate(),
        decided_at=datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc),
        actor_id=BusinessId("USR-0001"), acting_role=BusinessId("ROLE-QA"),
        correlation_id=CorrelationId("COR-00000001"), reason="Technische Prüfung bestanden.",
    )
    assert record.decision is KiCadReleaseDecision.APPROVED
    assert record.acting_role == BusinessId("ROLE-QA")
    assert record.reason == "Technische Prüfung bestanden."


def test_speichert_abgelehnte_entscheidung_und_gate_codes() -> None:
    record = repo().append(
        release_decision_id=BusinessId("REL-0002"), gate_result=gate(KiCadReleaseDecision.REJECTED),
        decided_at=datetime.now(timezone.utc), actor_id=BusinessId("USR-0001"),
        acting_role=BusinessId("ROLE-QA"), correlation_id=CorrelationId("COR-00000002"),
        reason="Freigabe wegen ungültigem Lauf abgelehnt.",
    )
    assert record.gate_finding_codes == ("ERR-KICAD-0068",)


def test_begruendung_ist_verpflichtend() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0075"):
        repo().append(
            release_decision_id=BusinessId("REL-0003"), gate_result=gate(),
            decided_at=datetime.now(timezone.utc), actor_id=BusinessId("USR-0001"),
            acting_role=BusinessId("ROLE-QA"), correlation_id=CorrelationId("COR-00000003"),
            reason="   ",
        )


def test_zeitpunkt_benoetigt_zeitzone() -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0074"):
        repo().append(
            release_decision_id=BusinessId("REL-0004"), gate_result=gate(),
            decided_at=datetime(2026, 8, 6, 12, 0), actor_id=BusinessId("USR-0001"),
            acting_role=BusinessId("ROLE-QA"), correlation_id=CorrelationId("COR-00000004"),
            reason="Prüfung bestanden.",
        )


def test_entscheidungen_sind_nur_anhaengbar_und_sortiert() -> None:
    repository = repo()
    for number, hour in ((1, 10), (2, 11)):
        repository.append(
            release_decision_id=BusinessId(f"REL-{number:04d}"), gate_result=gate(),
            decided_at=datetime(2026, 8, 6, hour, 0, tzinfo=timezone.utc),
            actor_id=BusinessId("USR-0001"), acting_role=BusinessId("ROLE-QA"),
            correlation_id=CorrelationId(f"COR-{number:08d}"), reason="Prüfung dokumentiert.",
        )
    assert [str(item.release_decision_id) for item in repository.list_for_project(BusinessId("PRJ-0001"))] == [
        "REL-0002", "REL-0001"
    ]
    with pytest.raises(ValueError, match="ERR-KICAD-0076"):
        repository.append(
            release_decision_id=BusinessId("REL-0001"), gate_result=gate(),
            decided_at=datetime.now(timezone.utc), actor_id=BusinessId("USR-0001"),
            acting_role=BusinessId("ROLE-QA"), correlation_id=CorrelationId("COR-00000005"),
            reason="Doppelter Eintrag.",
        )
