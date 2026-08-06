from datetime import datetime, timezone

import pytest

from projectos import (
    AuthorizedKiCadReleaseService,
    BusinessId,
    CorrelationId,
    KiCadQualityGateResult,
    KiCadReleaseDecision,
    KiCadValidationHistoryRecord,
    PERM_KICAD_RELEASE_DECIDE,
    ProjectActionAuthorizationService,
    ProjectAuthorityService,
    ProjectResponsibility,
    ProjectResponsibilityType,
    Role,
    SQLiteIdentityRepository,
    SQLiteKiCadReleaseAuditRepository,
    SQLiteProjectAuthorityPolicyRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 12, 30, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
USER = BusinessId("USR-LEADER")
DEPUTY = BusinessId("USR-DEPUTY")
ROLE = BusinessId("ROLE-KICAD-RELEASE")
WRONG_ROLE = BusinessId("ROLE-OBSERVER")


def gate_result() -> KiCadQualityGateResult:
    latest = KiCadValidationHistoryRecord(
        validation_id=BusinessId("KVAL-0001"),
        project_id=PROJECT,
        recorded_at=NOW,
        correlation_id=CorrelationId("COR-00000001"),
        valid=True,
        target_count=1,
        exception_count=0,
        findings=(),
        fingerprint="a" * 64,
    )
    return KiCadQualityGateResult(
        project_id=PROJECT,
        decision=KiCadReleaseDecision.APPROVED,
        evaluated_runs=1,
        latest_validation=latest,
        validity_rate=1.0,
        latest_error_count=0,
        latest_warning_count=0,
        latest_exception_count=0,
        findings=(),
    )


def configure(uow: SQLiteUnitOfWork, *, grant=True, role_permission=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(USER, "Projektleitung"))
    identities.upsert_user(UserAccount(DEPUTY, "Stellvertretung"))
    identities.upsert_role(Role(ROLE, frozenset({PERM_KICAD_RELEASE_DECIDE}) if role_permission else frozenset()))
    identities.upsert_role(Role(WRONG_ROLE, frozenset()))
    identities.assign_role(USER, ROLE)
    identities.assign_role(USER, WRONG_ROLE)
    identities.assign_role(DEPUTY, ROLE)

    responsibilities = SQLiteProjectResponsibilityRepository(uow.connection, identities)
    responsibilities.assign(ProjectResponsibility(
        PROJECT, ProjectResponsibilityType.PROJECT_LEADER, USER, NOW, reason="Projektleitung"
    ))
    responsibilities.assign(ProjectResponsibility(
        PROJECT, ProjectResponsibilityType.DEPUTY, DEPUTY, NOW, reason="Stellvertretung"
    ))
    policies = SQLiteProjectAuthorityPolicyRepository(uow.connection)
    permissions = frozenset({PERM_KICAD_RELEASE_DECIDE}) if grant else frozenset()
    policies.set_permissions(PROJECT, ProjectResponsibilityType.PROJECT_LEADER, permissions)
    policies.set_permissions(PROJECT, ProjectResponsibilityType.DEPUTY, permissions)
    authorization = ProjectActionAuthorizationService(
        ProjectAuthorityService(responsibilities), policies, identities
    )
    audit = SQLiteKiCadReleaseAuditRepository(uow.connection)
    return AuthorizedKiCadReleaseService(authorization, audit), audit


def test_autorisierte_freigabe_wird_mit_ermittelter_person_gespeichert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, audit = configure(uow)
        result = service.decide(
            release_decision_id=BusinessId("KREL-0001"),
            gate_result=gate_result(),
            decided_at=NOW,
            acting_role=ROLE,
            correlation_id=CorrelationId("COR-00000002"),
            reason="Technische Qualitätsgrenzen sind erfüllt.",
        )
        assert result.authorization.allowed
        assert result.record.actor_id == USER
        assert result.record.acting_role == ROLE
        assert audit.get(BusinessId("KREL-0001")) == result.record


def test_stellvertretung_kann_bei_abwesenheit_entscheiden(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _ = configure(uow)
        result = service.decide(
            release_decision_id=BusinessId("KREL-0002"), gate_result=gate_result(),
            decided_at=NOW, acting_role=ROLE,
            correlation_id=CorrelationId("COR-00000003"), reason="Vertretungsfreigabe.",
            unavailable_user_ids=frozenset({USER}),
        )
        assert result.record.actor_id == DEPUTY
        assert result.authorization.authority.source is ProjectResponsibilityType.DEPUTY


def test_fehlende_projektvollmacht_lehnt_ab_und_speichert_nichts(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, audit = configure(uow, grant=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0078"):
            service.decide(
                release_decision_id=BusinessId("KREL-0003"), gate_result=gate_result(),
                decided_at=NOW, acting_role=ROLE,
                correlation_id=CorrelationId("COR-00000004"), reason="Nicht zulässig.",
            )
        assert audit.list_for_project(PROJECT) == ()


def test_rolle_muss_die_freigabeberechtigung_tatsaechlich_erteilen(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, audit = configure(uow)
        with pytest.raises(PermissionError, match="ERR-KICAD-0079"):
            service.decide(
                release_decision_id=BusinessId("KREL-0004"), gate_result=gate_result(),
                decided_at=NOW, acting_role=WRONG_ROLE,
                correlation_id=CorrelationId("COR-00000005"), reason="Falsche Rolle.",
            )
        assert audit.list_for_project(PROJECT) == ()


def test_fehlende_rollenerlaubnis_lehnt_vor_persistenz_ab(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, audit = configure(uow, role_permission=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0078"):
            service.decide(
                release_decision_id=BusinessId("KREL-0005"), gate_result=gate_result(),
                decided_at=NOW, acting_role=ROLE,
                correlation_id=CorrelationId("COR-00000006"), reason="Keine Rollenberechtigung.",
            )
        assert audit.list_for_project(PROJECT) == ()
