from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    KiCadReleaseAttemptAlertResult,
    KiCadSecurityAlertFinding,
    KiCadSecurityAlertLevel,
    KiCadSecurityAlertStatus,
    SQLiteKiCadSecurityAlertRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 13, 0, tzinfo=timezone.utc)
ALERT_ID = BusinessId("KALERT-0001")
USER = BusinessId("USR-SECURITY")


def alert_result(level=KiCadSecurityAlertLevel.WARNING):
    return KiCadReleaseAttemptAlertResult(
        project_id=BusinessId("PRJ-0001"), evaluated_at=NOW,
        window_start=NOW - timedelta(hours=24), total_attempts=3, level=level,
        findings=(KiCadSecurityAlertFinding("WARN-KICAD-0002", level, "Schwelle erreicht."),),
    )


def test_alarm_durchlaeuft_offen_bestaetigt_abgeschlossen(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadSecurityAlertRepository(uow.connection)
        created = repo.create(
            alert_id=ALERT_ID, result=alert_result(), correlation_id=CorrelationId("COR-00000001")
        )
        assert created.status is KiCadSecurityAlertStatus.OPEN
        acknowledged = repo.acknowledge(
            ALERT_ID, acknowledged_at=NOW + timedelta(minutes=5), acknowledged_by=USER,
            reason="Alarm wurde geprüft.",
        )
        assert acknowledged.status is KiCadSecurityAlertStatus.ACKNOWLEDGED
        resolved = repo.resolve(
            ALERT_ID, resolved_at=NOW + timedelta(minutes=10), resolved_by=USER,
            reason="Ursache dokumentiert und Maßnahme abgeschlossen.",
        )
        assert resolved.status is KiCadSecurityAlertStatus.RESOLVED
        assert resolved.resolved_by == USER


def test_clear_ergebnis_wird_nicht_als_alarm_gespeichert(tmp_path) -> None:
    clear = KiCadReleaseAttemptAlertResult(
        None, NOW, NOW - timedelta(hours=1), 0, KiCadSecurityAlertLevel.CLEAR, ()
    )
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadSecurityAlertRepository(uow.connection)
        with pytest.raises(ValueError, match="ERR-KICAD-0100"):
            repo.create(alert_id=ALERT_ID, result=clear, correlation_id=CorrelationId("COR-00000002"))


def test_alarm_muss_vor_abschluss_bestaetigt_sein(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadSecurityAlertRepository(uow.connection)
        repo.create(alert_id=ALERT_ID, result=alert_result(), correlation_id=CorrelationId("COR-00000003"))
        with pytest.raises(ValueError, match="ERR-KICAD-0105"):
            repo.resolve(ALERT_ID, resolved_at=NOW + timedelta(minutes=1), resolved_by=USER, reason="Zu früh.")


def test_bearbeitung_benoetigt_zeitzone_und_begruendung(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadSecurityAlertRepository(uow.connection)
        repo.create(alert_id=ALERT_ID, result=alert_result(), correlation_id=CorrelationId("COR-00000004"))
        with pytest.raises(ValueError, match="ERR-KICAD-0108"):
            repo.acknowledge(ALERT_ID, acknowledged_at=datetime(2026, 8, 6, 13, 5), acknowledged_by=USER, reason="Prüfung")
        with pytest.raises(ValueError, match="ERR-KICAD-0109"):
            repo.acknowledge(ALERT_ID, acknowledged_at=NOW, acknowledged_by=USER, reason="  ")


def test_statuslisten_sind_getrennt_und_sortiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadSecurityAlertRepository(uow.connection)
        repo.create(alert_id=BusinessId("KALERT-0001"), result=alert_result(), correlation_id=CorrelationId("COR-00000005"))
        later = KiCadReleaseAttemptAlertResult(
            BusinessId("PRJ-0001"), NOW + timedelta(minutes=1), NOW - timedelta(hours=1), 5,
            KiCadSecurityAlertLevel.CRITICAL,
            (KiCadSecurityAlertFinding("ERR-KICAD-0096", KiCadSecurityAlertLevel.CRITICAL, "Kritisch."),),
        )
        repo.create(alert_id=BusinessId("KALERT-0002"), result=later, correlation_id=CorrelationId("COR-00000006"))
        repo.acknowledge(BusinessId("KALERT-0001"), acknowledged_at=NOW + timedelta(minutes=2), acknowledged_by=USER, reason="Übernommen")
        assert [item.alert_id for item in repo.list_for_status(KiCadSecurityAlertStatus.OPEN)] == [BusinessId("KALERT-0002")]
        assert [item.alert_id for item in repo.list_for_status(KiCadSecurityAlertStatus.ACKNOWLEDGED)] == [BusinessId("KALERT-0001")]
