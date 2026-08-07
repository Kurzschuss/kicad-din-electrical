from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    CorrelationId,
    KiCadReleaseAttemptAlertPolicy,
    KiCadReleaseAttemptAlertService,
    KiCadSecurityAlertLevel,
    SQLiteKiCadReleaseAttemptAuditRepository,
    SQLiteUnitOfWork,
)

NOW = datetime(2026, 8, 6, 13, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
ACTOR = BusinessId("USR-LEADER")
ROLE = BusinessId("ROLE-KICAD-RELEASE")
PERMISSION = BusinessId("PERM-KICAD-RELEASE-DECIDE")


def append(repo, number: int, *, minutes_ago: int, code: str = "ERR-KICAD-0078", actor=ACTOR, role=ROLE):
    repo.append(
        attempt_id=BusinessId(f"KATT-{number:04d}"),
        project_id=PROJECT,
        attempted_at=NOW - timedelta(minutes=minutes_ago),
        actor_id=actor,
        acting_role=role,
        permission_id=PERMISSION,
        denial_code=code,
        denial_reason="Autorisierung abgelehnt.",
        correlation_id=CorrelationId.from_sequence(number),
    )


def test_keine_ablehnungen_erzeugt_keinen_alarm(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        result = KiCadReleaseAttemptAlertService(uow.connection).evaluate(
            evaluated_at=NOW, project_id=PROJECT
        )
        assert result.level is KiCadSecurityAlertLevel.CLEAR
        assert not result.alert


def test_warnschwelle_wird_im_zeitfenster_erkannt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        for number in range(1, 4):
            append(repo, number, minutes_ago=number)
        result = KiCadReleaseAttemptAlertService(uow.connection).evaluate(
            evaluated_at=NOW, project_id=PROJECT
        )
        assert result.level is KiCadSecurityAlertLevel.WARNING
        assert any(item.code == "WARN-KICAD-0002" for item in result.findings)


def test_kritische_benutzerschwelle_hat_vorrang(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        for number in range(1, 6):
            append(repo, number, minutes_ago=number)
        result = KiCadReleaseAttemptAlertService(uow.connection).evaluate(
            evaluated_at=NOW,
            project_id=PROJECT,
            policy=KiCadReleaseAttemptAlertPolicy(
                warning_attempts=10,
                critical_attempts=20,
                warning_attempts_per_actor=3,
                critical_attempts_per_actor=5,
            ),
        )
        assert result.level is KiCadSecurityAlertLevel.CRITICAL
        assert any(item.code == "ERR-KICAD-0097" and item.subject_id == ACTOR for item in result.findings)


def test_kritischer_ablehnungscode_loest_alarm_aus(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        append(repo, 1, minutes_ago=1, code="ERR-KICAD-0079")
        result = KiCadReleaseAttemptAlertService(uow.connection).evaluate(
            evaluated_at=NOW,
            project_id=PROJECT,
            policy=KiCadReleaseAttemptAlertPolicy(
                warning_attempts=10,
                critical_attempts=20,
                critical_denial_codes=("err-kicad-0079",),
            ),
        )
        assert result.level is KiCadSecurityAlertLevel.CRITICAL
        assert any(item.code == "ERR-KICAD-0099" for item in result.findings)


def test_alte_versuche_liegen_ausserhalb_des_zeitfensters(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        repo = SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        append(repo, 1, minutes_ago=60 * 48)
        result = KiCadReleaseAttemptAlertService(uow.connection).evaluate(
            evaluated_at=NOW,
            project_id=PROJECT,
            policy=KiCadReleaseAttemptAlertPolicy(window=timedelta(hours=24)),
        )
        assert result.total_attempts == 0
        assert result.level is KiCadSecurityAlertLevel.CLEAR


def test_ungueltige_richtlinien_und_zeitpunkte_werden_abgelehnt(tmp_path) -> None:
    with pytest.raises(ValueError, match="ERR-KICAD-0090"):
        KiCadReleaseAttemptAlertPolicy(window=timedelta(0))
    with pytest.raises(ValueError, match="ERR-KICAD-0092"):
        KiCadReleaseAttemptAlertPolicy(warning_attempts=5, critical_attempts=4)
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        SQLiteKiCadReleaseAttemptAuditRepository(uow.connection)
        with pytest.raises(ValueError, match="ERR-KICAD-0095"):
            KiCadReleaseAttemptAlertService(uow.connection).evaluate(
                evaluated_at=datetime(2026, 8, 6, 13, 0), project_id=PROJECT
            )
