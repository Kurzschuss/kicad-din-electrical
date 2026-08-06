from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    GlobalSecurityResponsibilityDiagnostic,
    GlobalSecurityStaffingDecision,
    GlobalSecurityStaffingFinding,
    GlobalSecurityStaffingGateResult,
    SQLiteGlobalSecurityStaffingReleaseRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 16, 0, tzinfo=timezone.utc)


def gate(decision=GlobalSecurityStaffingDecision.APPROVED):
    findings = () if decision is GlobalSecurityStaffingDecision.APPROVED else (
        GlobalSecurityStaffingFinding("ERR-KICAD-0138", "Stellvertretung fehlt."),
    )
    return GlobalSecurityStaffingGateResult(
        decision,
        GlobalSecurityResponsibilityDiagnostic(None, None, False, False, False, False, 2, NOW),
        findings,
    )


def test_freigabeentscheidung_wird_unveraenderlich_gespeichert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
        record = repo.append(
            release_id=BusinessId("GSEC-RELEASE-0001"), gate_result=gate(), decided_at=NOW,
            actor_id=BusinessId("USR-AUDITOR"), acting_role=BusinessId("ROLE-SECURITY-AUDITOR"),
            reason="Besetzung technisch geprüft.", correlation_id=CorrelationId("COR-00000101"),
        )
        assert record.decision is GlobalSecurityStaffingDecision.APPROVED
        assert record.total_changes == 2
        assert repo.get(record.release_id) == record


def test_abgelehnte_entscheidung_speichert_finding_codes(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
        record = repo.append(
            release_id=BusinessId("GSEC-RELEASE-0002"), gate_result=gate(GlobalSecurityStaffingDecision.REJECTED),
            decided_at=NOW, actor_id=BusinessId("USR-AUDITOR"),
            acting_role=BusinessId("ROLE-SECURITY-AUDITOR"), reason="Stellvertretung fehlt.",
            correlation_id=CorrelationId("COR-00000102"),
        )
        assert record.finding_codes == ("ERR-KICAD-0138",)


def test_doppelte_kennung_wird_abgelehnt(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
        kwargs = dict(
            release_id=BusinessId("GSEC-RELEASE-0003"), gate_result=gate(), decided_at=NOW,
            actor_id=BusinessId("USR-AUDITOR"), acting_role=BusinessId("ROLE-SECURITY-AUDITOR"),
            reason="Geprüft.", correlation_id=CorrelationId("COR-00000103"),
        )
        repo.append(**kwargs)
        with pytest.raises(ValueError, match="ERR-KICAD-0144"):
            repo.append(**kwargs)


def test_zeitpunkt_und_begruendung_sind_verpflichtend(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
        with pytest.raises(ValueError, match="ERR-KICAD-0142"):
            repo.append(
                release_id=BusinessId("GSEC-RELEASE-0004"), gate_result=gate(),
                decided_at=datetime(2026, 8, 6, 16, 0), actor_id=BusinessId("USR-AUDITOR"),
                acting_role=BusinessId("ROLE-SECURITY-AUDITOR"), reason="Geprüft.",
                correlation_id=CorrelationId("COR-00000104"),
            )
        with pytest.raises(ValueError, match="ERR-KICAD-0143"):
            repo.append(
                release_id=BusinessId("GSEC-RELEASE-0005"), gate_result=gate(), decided_at=NOW,
                actor_id=BusinessId("USR-AUDITOR"), acting_role=BusinessId("ROLE-SECURITY-AUDITOR"),
                reason=" ", correlation_id=CorrelationId("COR-00000105"),
            )


def test_historie_ist_neueste_zuerst_sortiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
        for index in (1, 2):
            repo.append(
                release_id=BusinessId(f"GSEC-RELEASE-001{index}"), gate_result=gate(),
                decided_at=NOW.replace(minute=index), actor_id=BusinessId("USR-AUDITOR"),
                acting_role=BusinessId("ROLE-SECURITY-AUDITOR"), reason="Geprüft.",
                correlation_id=CorrelationId(f"COR-0000011{index}"),
            )
        assert [str(item.release_id) for item in repo.list_all()] == ["GSEC-RELEASE-0012", "GSEC-RELEASE-0011"]
