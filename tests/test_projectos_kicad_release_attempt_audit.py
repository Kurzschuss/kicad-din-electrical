from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from projectos import (
    AuthorizedKiCadReleaseService,
    BusinessId,
    CorrelationId,
    KiCadQualityGateResult,
    KiCadReleaseDecision,
    SQLiteKiCadReleaseAttemptAuditRepository,
    SQLiteKiCadReleaseAuditRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 12, 45, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
USER = BusinessId("USR-LEADER")
ROLE = BusinessId("ROLE-KICAD-RELEASE")


def gate_result() -> KiCadQualityGateResult:
    return KiCadQualityGateResult(
        project_id=PROJECT,
        decision=KiCadReleaseDecision.INSUFFICIENT_DATA,
        evaluated_runs=0,
        latest_validation=None,
        validity_rate=0.0,
        latest_error_count=0,
        latest_warning_count=0,
        latest_exception_count=0,
        findings=(),
    )


class DeniedAuthorization:
    def authorize(self, project_id, permission, **kwargs):
        return SimpleNamespace(
            allowed=False,
            reason="Projektfunktion besitzt keine Freigabevollmacht.",
            authority=SimpleNamespace(authorized_user=SimpleNamespace(user_id=USER)),
            authorization=None,
        )


class WrongRoleAuthorization:
    def authorize(self, project_id, permission, **kwargs):
        return SimpleNamespace(
            allowed=True,
            reason="Autorisierung erlaubt.",
            authority=SimpleNamespace(authorized_user=SimpleNamespace(user_id=USER)),
            authorization=SimpleNamespace(matched_roles=(BusinessId("ROLE-OTHER"),)),
        )


def service(uow, authorization):
    releases = SQLiteKiCadReleaseAuditRepository(uow.connection)
    attempts = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
    return AuthorizedKiCadReleaseService(authorization, releases, attempts), releases, attempts


def test_abgelehnte_projektvollmacht_wird_auditiert_aber_nicht_freigegeben(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        api, releases, attempts = service(uow, DeniedAuthorization())
        with pytest.raises(PermissionError, match="ERR-KICAD-0078"):
            api.decide(
                release_decision_id=BusinessId("KREL-1001"),
                attempt_id=BusinessId("KATT-1001"),
                gate_result=gate_result(),
                decided_at=NOW,
                acting_role=ROLE,
                correlation_id=CorrelationId("COR-00000101"),
                reason="Freigabeversuch.",
            )
        assert releases.list_for_project(PROJECT) == ()
        record = attempts.get(BusinessId("KATT-1001"))
        assert record.denial_code == "ERR-KICAD-0078"
        assert record.actor_id == USER


def test_unpassende_rolle_wird_mit_eigenem_code_auditiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        api, releases, attempts = service(uow, WrongRoleAuthorization())
        with pytest.raises(PermissionError, match="ERR-KICAD-0079"):
            api.decide(
                release_decision_id=BusinessId("KREL-1002"),
                attempt_id=BusinessId("KATT-1002"),
                gate_result=gate_result(),
                decided_at=NOW,
                acting_role=ROLE,
                correlation_id=CorrelationId("COR-00000102"),
                reason="Freigabeversuch.",
            )
        assert releases.list_for_project(PROJECT) == ()
        assert attempts.get(BusinessId("KATT-1002")).denial_code == "ERR-KICAD-0079"


def test_aktiviertes_versuchsaudit_benoetigt_eine_kennung(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        api, _, attempts = service(uow, DeniedAuthorization())
        with pytest.raises(ValueError, match="ERR-KICAD-0085"):
            api.decide(
                release_decision_id=BusinessId("KREL-1003"), gate_result=gate_result(),
                decided_at=NOW, acting_role=ROLE,
                correlation_id=CorrelationId("COR-00000103"), reason="Freigabeversuch.",
            )
        assert attempts.list_for_project(PROJECT) == ()


def test_versuchsaudit_ist_nur_anhaengbar_und_chronologisch(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        attempts = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        for number, minute in ((1, 1), (2, 2)):
            attempts.append(
                attempt_id=BusinessId(f"KATT-200{number}"), project_id=PROJECT,
                attempted_at=NOW.replace(minute=minute), actor_id=USER, acting_role=ROLE,
                permission_id=BusinessId("PERM-KICAD-RELEASE-DECIDE"),
                denial_code="ERR-KICAD-0078", denial_reason="Abgelehnt.",
                correlation_id=CorrelationId(f"COR-0000020{number}"),
            )
        assert [item.attempt_id for item in attempts.list_for_project(PROJECT)] == [
            BusinessId("KATT-2002"), BusinessId("KATT-2001")
        ]
        with pytest.raises(ValueError, match="ERR-KICAD-0083"):
            attempts.append(
                attempt_id=BusinessId("KATT-2001"), project_id=PROJECT, attempted_at=NOW,
                actor_id=USER, acting_role=ROLE,
                permission_id=BusinessId("PERM-KICAD-RELEASE-DECIDE"),
                denial_code="ERR-KICAD-0078", denial_reason="Doppelt.",
                correlation_id=CorrelationId("COR-00000203"),
            )
