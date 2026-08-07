from datetime import datetime, timezone

from projectos import (
    AuditedProjectActionService,
    BusinessId,
    Command,
    CorrelationId,
    ObjectId,
    ProjectActionAuthorizationService,
    ProjectAuthorityService,
    ProjectCommandDefinition,
    ProjectCommandPipeline,
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

NOW = datetime(2026, 8, 6, 9, 30, tzinfo=timezone.utc)
PROJECT = BusinessId("PRJ-0001")
USER = BusinessId("USR-LEADER")
ROLE = BusinessId("ROLE-PROJECT")
PERMISSION = BusinessId("PERM-PROJECT-CHANGE")
OBJECT_ID = ObjectId.new()
COMMAND_TYPE = "project.setting.change"


def configure(uow: SQLiteUnitOfWork, *, blacklist: bool = False) -> ProjectCommandPipeline:
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
        ProjectAuthorityService(responsibilities), policies, identities
    )
    actions = AuditedProjectActionService(
        authorization, SQLiteAuditRepository(uow.connection)
    )
    return ProjectCommandPipeline(actions)


def command(sequence: int = 50) -> Command:
    return Command(
        BusinessId(f"CMD-PRJ-{sequence:04d}"),
        COMMAND_TYPE,
        CorrelationId.from_sequence(sequence),
        issued_at=NOW,
        payload={"value": "neu"},
    )


def test_command_wird_autorisiert_auditiert_und_ausgefuehrt(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = configure(uow)
        pipeline.register(
            ProjectCommandDefinition(COMMAND_TYPE, PERMISSION, "project_setting_changed"),
            lambda item: item.payload["value"],
        )
        result = pipeline.dispatch(
            command(),
            project_id=PROJECT,
            project_object_id=OBJECT_ID,
            audit_id=BusinessId("AUD-CMD-0001"),
            reason="Projektwert ändern",
        )
        assert result.is_success
        assert result.value is not None
        assert result.value.executed
        assert result.value.value == "neu"
        assert result.correlation_id == CorrelationId.from_sequence(50)


def test_abgelehnter_command_liefert_strukturierten_fehler_und_wird_auditiert(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = configure(uow, blacklist=True)
        pipeline.register(
            ProjectCommandDefinition(COMMAND_TYPE, PERMISSION, "project_setting_changed"),
            lambda item: item.payload["value"],
        )
        result = pipeline.dispatch(
            command(51),
            project_id=PROJECT,
            project_object_id=OBJECT_ID,
            audit_id=BusinessId("AUD-CMD-0002"),
            reason="Gesperrten Wert ändern",
        )
        assert not result.is_success
        assert result.errors[0].code == BusinessId("ERR-PRJ-CMD-0003")
        assert len(SQLiteAuditRepository(uow.connection).all()) == 1


def test_nicht_registrierter_command_liefert_fehler(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = configure(uow).dispatch(
            command(52),
            project_id=PROJECT,
            project_object_id=OBJECT_ID,
            audit_id=BusinessId("AUD-CMD-0003"),
            reason="Test",
        )
        assert not result.is_success
        assert result.errors[0].code == BusinessId("ERR-PRJ-CMD-0001")


def test_doppelte_registrierung_wird_abgewiesen(tmp_path) -> None:
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        pipeline = configure(uow)
        definition = ProjectCommandDefinition(COMMAND_TYPE, PERMISSION, "project_setting_changed")
        pipeline.register(definition, lambda item: None)
        try:
            pipeline.register(definition, lambda item: None)
        except ValueError as exc:
            assert "bereits" in str(exc)
        else:
            raise AssertionError("Doppelte Registrierung wurde nicht abgewiesen.")
