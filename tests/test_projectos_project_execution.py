from datetime import datetime, timezone

import pytest

from projectos import (
    AuditedProjectActionService,
    BusinessId,
    CorrelationId,
    ObjectId,
    ProjectActionAuthorizationService,
    ProjectAuthorityService,
    ProjectResponsibility,
    ProjectResponsibilityType,
    Role,
    SQLiteAuditRepository,
    SQLiteIdentityRepository,
    SQLiteProjectAuthorityPolicyRepository,
    SQLiteProjectResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 9, 0, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
USER = BusinessId("USR-LEADER")
ROLE = BusinessId("ROLE-PROJECT")
PERMISSION = BusinessId("PERM-PROJECT-CHANGE")
OBJECT_ID = ObjectId.new()


def configure(uow: SQLiteUnitOfWork, *, blacklist: bool = False) -> AuditedProjectActionService:
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(USER, "Projektleitung"))
    identities.upsert_role(Role(ROLE, frozenset({PERMISSION})))
    identities.assign_role(USER, ROLE)
    if blacklist:
        identities.set_blacklist(USER, frozenset({PERMISSION}))

    responsibilities = SQLiteProjectResponsibilityRepository(uow.connection, identities)
    responsibilities.assign(
        ProjectResponsibility(
            PROJECT,
            ProjectResponsibilityType.PROJECT_LEADER,
            USER,
            NOW,
            reason="Projektstart",
        )
    )
    policies = SQLiteProjectAuthorityPolicyRepository(uow.connection)
    policies.set_permissions(
        PROJECT,
        ProjectResponsibilityType.PROJECT_LEADER,
        frozenset({PERMISSION}),
    )
    authorization = ProjectActionAuthorizationService(
        ProjectAuthorityService(responsibilities),
        policies,
        identities,
    )
    return AuditedProjectActionService(authorization, SQLiteAuditRepository(uow.connection))


def test_erlaubte_handlung_wird_ausgefuehrt_und_auditiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    calls: list[str] = []
    with SQLiteUnitOfWork(database) as uow:
        service = configure(uow)
        result = service.execute(
            PROJECT,
            PERMISSION,
            at=NOW,
            audit_id=BusinessId("AUD-PRJ-0001"),
            correlation_id=CorrelationId.from_sequence(49),
            project_object_id=OBJECT_ID,
            action="project_setting_changed",
            reason="Freigegebene Projektänderung",
            operation=lambda: calls.append("ausgefuehrt") or "ok",
        )
        assert result.executed is True
        assert result.value == "ok"
        assert result.audit_entry.new_values["execution_status"] == "EXECUTED"
    assert calls == ["ausgefuehrt"]

    with SQLiteUnitOfWork(database) as uow:
        entries = SQLiteAuditRepository(uow.connection).all()
        assert len(entries) == 1
        assert entries[0].permission_id == PERMISSION


def test_abgelehnte_handlung_wird_nicht_ausgefuehrt_aber_auditiert(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    calls: list[str] = []
    with SQLiteUnitOfWork(database) as uow:
        service = configure(uow, blacklist=True)
        result = service.execute(
            PROJECT,
            PERMISSION,
            at=NOW,
            audit_id=BusinessId("AUD-PRJ-0002"),
            correlation_id=CorrelationId.from_sequence(50),
            project_object_id=OBJECT_ID,
            action="project_setting_changed",
            reason="Versuchte Projektänderung",
            operation=lambda: calls.append("nicht erlaubt"),
        )
        assert result.executed is False
        assert result.audit_entry.new_values["execution_status"] == "DENIED"
    assert calls == []


def test_fehler_der_handlung_rollt_audit_eintrag_zurueck(tmp_path) -> None:
    database = tmp_path / "projectos.db"
    with pytest.raises(RuntimeError, match="Fachfehler"):
        with SQLiteUnitOfWork(database) as uow:
            service = configure(uow)

            def fail() -> None:
                raise RuntimeError("Fachfehler")

            service.execute(
                PROJECT,
                PERMISSION,
                at=NOW,
                audit_id=BusinessId("AUD-PRJ-0003"),
                correlation_id=CorrelationId.from_sequence(51),
                project_object_id=OBJECT_ID,
                action="project_setting_changed",
                reason="Fehlschlagende Projektänderung",
                operation=fail,
            )

    with SQLiteUnitOfWork(database) as uow:
        assert SQLiteAuditRepository(uow.connection).all() == ()


def test_ausfuehrungszeitpunkt_benoetigt_zeitzone(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service = configure(uow)
        with pytest.raises(ValueError, match="Zeitzonenbezug"):
            service.execute(
                PROJECT,
                PERMISSION,
                at=datetime(2026, 8, 6, 9, 0),
                audit_id=BusinessId("AUD-PRJ-0004"),
                correlation_id=CorrelationId.from_sequence(52),
                project_object_id=OBJECT_ID,
                action="project_setting_changed",
                reason="Test",
                operation=lambda: None,
            )
