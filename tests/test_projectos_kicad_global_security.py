from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    AuthorizedGlobalKiCadSecurityAlertService,
    BusinessId,
    CorrelationId,
    GlobalSecurityResponsibility,
    GlobalSecurityResponsibilityType,
    KiCadReleaseAttemptAlertResult,
    KiCadSecurityAlertFinding,
    KiCadSecurityAlertLevel,
    KiCadSecurityAlertStatus,
    PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE,
    PERM_KICAD_SECURITY_ALERT_RESOLVE,
    Role,
    SQLiteGlobalKiCadSecurityAlertActionAuditRepository,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteIdentityRepository,
    SQLiteKiCadSecurityAlertRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 14, 0, tzinfo=timezone.utc)
PRIMARY = BusinessId("USR-SECURITY")
DEPUTY = BusinessId("USR-SECURITY-DEPUTY")
ROLE = BusinessId("ROLE-GLOBAL-SECURITY")
WRONG_ROLE = BusinessId("ROLE-OBSERVER")
ALERT = BusinessId("KALERT-GLOBAL-0001")


def alert_result(project_id=None):
    return KiCadReleaseAttemptAlertResult(
        project_id=project_id,
        evaluated_at=NOW,
        window_start=NOW - timedelta(hours=24),
        total_attempts=5,
        level=KiCadSecurityAlertLevel.CRITICAL,
        findings=(KiCadSecurityAlertFinding(
            "ERR-KICAD-0096", KiCadSecurityAlertLevel.CRITICAL, "Kritische Schwelle erreicht."
        ),),
    )


def configure(uow, *, role_permissions=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY, "Globale Sicherheitsverantwortung"))
    identities.upsert_user(UserAccount(DEPUTY, "Globale Sicherheitsvertretung"))
    permissions = frozenset({PERM_KICAD_SECURITY_ALERT_ACKNOWLEDGE, PERM_KICAD_SECURITY_ALERT_RESOLVE}) if role_permissions else frozenset()
    identities.upsert_role(Role(ROLE, permissions))
    identities.upsert_role(Role(WRONG_ROLE, frozenset()))
    identities.assign_role(PRIMARY, ROLE)
    identities.assign_role(PRIMARY, WRONG_ROLE)
    identities.assign_role(DEPUTY, ROLE)
    responsibilities = SQLiteGlobalSecurityResponsibilityRepository(uow.connection, identities)
    responsibilities.assign(GlobalSecurityResponsibility(
        GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Globale Sicherheitsleitung"
    ))
    responsibilities.assign(GlobalSecurityResponsibility(
        GlobalSecurityResponsibilityType.DEPUTY, DEPUTY, NOW, "Globale Vertretung"
    ))
    alerts = SQLiteKiCadSecurityAlertRepository(uow.connection)
    alerts.create(alert_id=ALERT, result=alert_result(), correlation_id=CorrelationId("COR-GLOBAL-0001"))
    audit = SQLiteGlobalKiCadSecurityAlertActionAuditRepository(uow.connection)
    return AuthorizedGlobalKiCadSecurityAlertService(responsibilities, identities, alerts, audit), alerts, audit


def test_globale_verantwortung_bestaetigt_und_schliesst_projektlosen_alarm(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        acknowledged = service.acknowledge(
            ALERT, action_id=BusinessId("KACT-G-0001"), acknowledged_at=NOW,
            acting_role=ROLE, reason="Global geprüft.", correlation_id=CorrelationId("COR-GLOBAL-0002")
        )
        assert acknowledged.authority.source is GlobalSecurityResponsibilityType.PRIMARY
        assert acknowledged.alert.status is KiCadSecurityAlertStatus.ACKNOWLEDGED
        resolved = service.resolve(
            ALERT, action_id=BusinessId("KACT-G-0002"), resolved_at=NOW + timedelta(minutes=5),
            acting_role=ROLE, reason="Global abgeschlossen.", correlation_id=CorrelationId("COR-GLOBAL-0003")
        )
        assert resolved.alert.status is KiCadSecurityAlertStatus.RESOLVED
        assert len(audit.list_for_alert(ALERT)) == 2
        assert alerts.get(ALERT).resolved_by == PRIMARY


def test_stellvertretung_uebernimmt_bei_abwesenheit(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _, _ = configure(uow)
        result = service.acknowledge(
            ALERT, action_id=BusinessId("KACT-G-0003"), acknowledged_at=NOW,
            acting_role=ROLE, reason="Vertretung übernimmt.", correlation_id=CorrelationId("COR-GLOBAL-0004"),
            unavailable_user_ids=frozenset({PRIMARY}),
        )
        assert result.authority.source is GlobalSecurityResponsibilityType.DEPUTY
        assert result.alert.acknowledged_by == DEPUTY


def test_falsche_rolle_lehnt_ab_und_veraendert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        with pytest.raises(PermissionError, match="ERR-KICAD-0128"):
            service.acknowledge(
                ALERT, action_id=BusinessId("KACT-G-0004"), acknowledged_at=NOW,
                acting_role=WRONG_ROLE, reason="Falsche Rolle.", correlation_id=CorrelationId("COR-GLOBAL-0005")
            )
        assert alerts.get(ALERT).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(ALERT) == ()


def test_fehlende_rollenerlaubnis_lehnt_ab(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow, role_permissions=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0127"):
            service.acknowledge(
                ALERT, action_id=BusinessId("KACT-G-0005"), acknowledged_at=NOW,
                acting_role=ROLE, reason="Keine Berechtigung.", correlation_id=CorrelationId("COR-GLOBAL-0006")
            )
        assert alerts.get(ALERT).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(ALERT) == ()


def test_projektbezogener_alarm_darf_nicht_global_bearbeitet_werden(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, alerts, audit = configure(uow)
        project_alert = BusinessId("KALERT-PROJECT-0001")
        alerts.create(
            alert_id=project_alert,
            result=alert_result(BusinessId("PRJ-0001")),
            correlation_id=CorrelationId("COR-GLOBAL-0007"),
        )
        with pytest.raises(ValueError, match="ERR-KICAD-0126"):
            service.acknowledge(
                project_alert, action_id=BusinessId("KACT-G-0006"), acknowledged_at=NOW,
                acting_role=ROLE, reason="Nicht global.", correlation_id=CorrelationId("COR-GLOBAL-0008")
            )
        assert alerts.get(project_alert).status is KiCadSecurityAlertStatus.OPEN
        assert audit.list_for_alert(project_alert) == ()
