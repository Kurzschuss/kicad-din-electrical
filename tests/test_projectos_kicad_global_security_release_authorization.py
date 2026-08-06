from datetime import datetime, timezone

import pytest

from projectos import (
    AuthorizedGlobalSecurityStaffingReleaseService,
    BusinessId,
    CorrelationId,
    GlobalSecurityResponsibility,
    GlobalSecurityResponsibilityHistoryService,
    GlobalSecurityResponsibilityType,
    GlobalSecurityStaffingQualityGate,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE,
    Role,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteGlobalSecurityStaffingReleaseRepository,
    SQLiteIdentityRepository,
    SQLiteTrackedGlobalSecurityResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 15, 30, tzinfo=timezone.utc)
PRIMARY = BusinessId("USR-SECURITY")
DEPUTY = BusinessId("USR-SECURITY-DEPUTY")
ROLE = BusinessId("ROLE-SECURITY-RELEASE")
WRONG_ROLE = BusinessId("ROLE-OBSERVER")


def configure(uow, *, grant_permission=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY, "Globale Sicherheitsleitung"))
    identities.upsert_user(UserAccount(DEPUTY, "Globale Sicherheitsvertretung"))
    permissions = (
        frozenset({PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE})
        if grant_permission else frozenset()
    )
    identities.upsert_role(Role(ROLE, permissions))
    identities.upsert_role(Role(WRONG_ROLE, frozenset()))
    identities.assign_role(PRIMARY, ROLE)
    identities.assign_role(PRIMARY, WRONG_ROLE)
    identities.assign_role(DEPUTY, ROLE)

    tracked = SQLiteTrackedGlobalSecurityResponsibilityRepository(uow.connection, identities)
    tracked.assign_tracked(
        GlobalSecurityResponsibility(
            GlobalSecurityResponsibilityType.PRIMARY,
            PRIMARY,
            NOW,
            "Hauptverantwortung",
        ),
        change_id=BusinessId("GSEC-CHANGE-1001"),
    )
    tracked.assign_tracked(
        GlobalSecurityResponsibility(
            GlobalSecurityResponsibilityType.DEPUTY,
            DEPUTY,
            NOW,
            "Stellvertretung",
        ),
        change_id=BusinessId("GSEC-CHANGE-1002"),
    )
    gate_result = GlobalSecurityStaffingQualityGate(
        GlobalSecurityResponsibilityHistoryService(uow.connection, identities)
    ).evaluate()
    responsibilities = SQLiteGlobalSecurityResponsibilityRepository(uow.connection, identities)
    releases = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
    service = AuthorizedGlobalSecurityStaffingReleaseService(
        responsibilities,
        identities,
        releases,
    )
    return service, releases, gate_result


def test_hauptverantwortung_darf_freigabe_speichern(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, releases, gate_result = configure(uow)
        result = service.decide(
            release_id=BusinessId("GSEC-REL-1001"),
            gate_result=gate_result,
            decided_at=NOW,
            acting_role=ROLE,
            reason="Besetzung technisch geprüft.",
            correlation_id=CorrelationId("COR-00001001"),
        )
        assert result.release_record.actor_id == PRIMARY
        assert result.release_record.acting_role == ROLE
        assert releases.get(BusinessId("GSEC-REL-1001")) == result.release_record


def test_stellvertretung_uebernimmt_bei_abwesenheit(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, _, gate_result = configure(uow)
        result = service.decide(
            release_id=BusinessId("GSEC-REL-1002"),
            gate_result=gate_result,
            decided_at=NOW,
            acting_role=ROLE,
            reason="Vertretung entscheidet.",
            correlation_id=CorrelationId("COR-00001002"),
            unavailable_user_ids=frozenset({PRIMARY}),
        )
        assert result.release_record.actor_id == DEPUTY
        assert result.authority.source is GlobalSecurityResponsibilityType.DEPUTY


def test_falsche_rolle_lehnt_ab_und_speichert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, releases, gate_result = configure(uow)
        with pytest.raises(PermissionError, match="ERR-KICAD-0147"):
            service.decide(
                release_id=BusinessId("GSEC-REL-1003"),
                gate_result=gate_result,
                decided_at=NOW,
                acting_role=WRONG_ROLE,
                reason="Falsche Rolle.",
                correlation_id=CorrelationId("COR-00001003"),
            )
        assert releases.list_all() == ()


def test_fehlende_berechtigung_lehnt_ab_und_speichert_nichts(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, releases, gate_result = configure(uow, grant_permission=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0146"):
            service.decide(
                release_id=BusinessId("GSEC-REL-1004"),
                gate_result=gate_result,
                decided_at=NOW,
                acting_role=ROLE,
                reason="Keine Berechtigung.",
                correlation_id=CorrelationId("COR-00001004"),
            )
        assert releases.list_all() == ()


def test_unverfuegbare_haupt_und_stellvertretung_lehnen_ab(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        service, releases, gate_result = configure(uow)
        with pytest.raises(LookupError, match="ERR-KICAD-0122"):
            service.decide(
                release_id=BusinessId("GSEC-REL-1005"),
                gate_result=gate_result,
                decided_at=NOW,
                acting_role=ROLE,
                reason="Niemand verfügbar.",
                correlation_id=CorrelationId("COR-00001005"),
                unavailable_user_ids=frozenset({PRIMARY, DEPUTY}),
            )
        assert releases.list_all() == ()
