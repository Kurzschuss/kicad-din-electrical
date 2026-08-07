from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    AuthorizedKiCadSecurityAlertService,
    BusinessId,
    CorrelationId,
    KiCadReleaseAttemptAlertResult,
    KiCadSecurityAlertFinding,
    KiCadSecurityAlertLevel,
    KiCadSecurityAlertStatus,
    PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE,
    PERM_KICAD_SECURITY_ALERT_RESOLVE,
    ProjectActionAuthorizationService,
    ProjectAuthorityService,
    ProjectResponsibility,
    ProjectResponsibilityType,
    Role,
    SQLiteIdentityRepository,
    SQLiteKiCadSecurityAlertActionAuditRepository,
    SQLiteKiCadSecurityAlertRepository,
    SQLiteProjectAuthorityPolicyRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 13, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
LEADER = BusinessId("USR-LEADER")
DEPUTY = BusinessId("USR-DEPUTY")
ROLE = BusinessId("ROLE-SECURITY")
WRONG_ROLE = BusinessId("ROLE-OBSERVER")
ALERT = BusinessId("KALERT-0001")


def alert_result(project_id=PROJECT):
    return KiCadReleaseAttemptAlertResult(
        project_id=project_id,
        evaluated_at=NOW,
        window_start=NOW - timedelta(hours=24),
        total_attempts=5,
        level=KiCadSecurityAlertLevel.CRITICAL,
        findings=(KiCadSecurityAlertFinding(
            "ERR-KICAD-0096", KiCadSecurityAlertLevel.CRITICAL, "Schwelle erreicht."
        ),),
    )


def configure(uow, *, grant=True, role_permissions=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(LEADER, "Projektleitung"))
    identities.upsert_user(UserAccount(DEPUTY, "Stellvertretung"))
    permissions = (
        frozenset({PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE, PERM_KICAD_SECURITY_ALERT_RESOLVE})
        if role_permissions else frozenset()
    )
    identities.upsert_role(Role(ROLE, permissions))
    identities.upsert_role(Role(WRONG_ROLE, frozenset()))
    for user in (LEADER, DEPUTY):
        identities.assign_role(user, ROLE)
    identities.assign_role(LEADER, WRONG_ROLE)

    responsibilities = SQLiteProjectResponsibilityRepository(uow.connection, identities)
    responsibilities.assign(ProjectResponsibility(
        PROJECT, ProjectResponsibilityType.PROJECT_LEADER, LEADER, NOW, reason="Projektleitung"
    ))
    responsibilities.assign(ProjectResponsibility(
        PROJECT, ProjectResponsibilityType.DEPUTY, DEPUTY, NOW, reason="Stellvertretung"
    ))
    policies = SQLiteProjectAuthorityPolicyRepository(uow.connection)
    project_permissions = permissions if grant else frozenset()
    policies.set_permissions(PROJECT, ProjectResponsibilityType.PROJECT_LEADER, project_permissions)
    policies.set_permissions(PROJECT, ProjectResponsibilityType.DEPUTY, project_permissions)

    alerts = SQLiteKiCadSecurityAlertRepository(uow.connection)
    alerts.create(alert_id=ALERT, result=alert_result(), correlation_id=CorrelationId("COR-00000001"))
    audit = SQLiteKiCadSecurityAlertActionAuditRepository(uow.connection)
    authorization = ProjectActionAuthorizationService(
        ProjectAuthorityService(responsibilities), policies, identities
    )
    return AuthorizedKiCadSecurityAlertService(authorization, alerts, audit), alerts, audit


def test_bestaetigung_und_abschluss_werden_autorisiert_und_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        acknowledged = service.acknowledge(
            ALERT, action_id=BusinessId("KACT-0001"), acknowledged_at=NOW + timedelta(minutes=5),
            acting_role=ROLE, reason="Alarm geprüft.", correlation_id=CorrelationId("COR-00000002"),
        )
        resolved = service.resolve(
            ALERT, action_id=BusinessId("KACT-0002"), resolved_at=NOW + timedelta(minutes=10),
            acting_role=ROLE, reason="Ursache geklärt.", correlation_id=CorrelationId("COR-00000003"),
        )
        assert acknowledged.alert.status is KiCadSecurityAlertStatus.ACKNOWLEDGED
        assert resolved.alert.status is KiCadSecurityAlertStatus.RESOLVED
        assert resolved.alert.resolved_by == LEADER
        assert [item.action.value for item in audit.list_for_alert(ALERT)] == ["ACKNOWLEDGE", "RESOLVE"]
        assert alerts.get(ALERT) == resolved.alert


def test_stellvertretung_kann_alarm_bestaetigen(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _, _ = configure(uow)
        result = service.acknowledge(
            ALERT, action_id=BusinessId("KACT-0003"), acknowledged_at=NOW + timedelta(minutes=5),
            acting_role=ROLE, reason="Vertretungsprüfung.", correlation_id=CorrelationId("COR-00000004"),
            unavailable_user_ids=frozenset({LEADER}),
        )
        assert result.alert.acknowledged_by == DEPUTY
        assert result.authorization.authority.source is ProjectResponsibilityType.DEPUTY


def test_fehlende_projektvollmacht_aendert_alarm_und_audit_nicht(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow, grant=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0115"):
            service.acknowledge(
                ALERT, action_id=BusinessId("KACT-0004"), acknowledged_at=NOW + timedelta(minutes=5),
                acting_role=ROLE, reason="Nicht erlaubt.", correlation_id=CorrelationId("COR-00000005"),
            )
        assert alerts.get(ALERT).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(ALERT) == ()


def test_handelnde_rolle_muss_berechtigung_tatsaechlich_erteilen(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        with pytest.raises(PermissionError, match="ERR-KICAD-0116"):
            service.acknowledge(
                ALERT, action_id=BusinessId("KACT-0005"), acknowledged_at=NOW + timedelta(minutes=5),
                acting_role=WRONG_ROLE, reason="Falsche Rolle.", correlation_id=CorrelationId("COR-00000006"),
            )
        assert alerts.get(ALERT).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(ALERT) == ()


def test_projektloser_alarm_wird_nicht_projektbezogen_autorisiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        global_alert = BusinessId("KALERT-GLOBAL")
        alerts.create(
            alert_id=global_alert, result=alert_result(None),
            correlation_id=CorrelationId("COR-00000007"),
        )
        with pytest.raises(ValueError, match="ERR-KICAD-0114"):
            service.acknowledge(
                global_alert, action_id=BusinessId("KACT-0006"),
                acknowledged_at=NOW + timedelta(minutes=5), acting_role=ROLE,
                reason="Projektlos.", correlation_id=CorrelationId("COR-00000008"),
            )
        assert alerts.get(global_alert).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(global_alert) == ()
