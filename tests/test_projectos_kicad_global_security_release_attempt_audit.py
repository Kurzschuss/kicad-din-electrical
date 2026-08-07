from datetime import datetime, timezone

import pytest

from projectos import (
    AuthorizedGlobalSecurityStaffingReleaseService, BusinessId, CorrelationId,
    GlobalSecurityResponsibility, GlobalSecurityResponsibilityHistoryService,
    GlobalSecurityResponsibilityType, GlobalSecurityStaffingQualityGate,
    PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE, Role,
    SQLiteGlobalSecurityResponsibilityRepository,
    SQLiteGlobalSecurityStaffingReleaseAttemptRepository,
    SQLiteGlobalSecurityStaffingReleaseRepository, SQLiteIdentityRepository,
    SQLiteTrackedGlobalSecurityResponsibilityRepository, SQLiteUnitOfWork, UserAccount,
)

NOW = datetime(2026, 8, 6, 16, 0, tzinfo=timezone.utc)
PRIMARY = BusinessId("USR-SECURITY")
DEPUTY = BusinessId("USR-SECURITY-DEPUTY")
ROLE = BusinessId("ROLE-SECURITY-RELEASE")
WRONG_ROLE = BusinessId("ROLE-OBSERVER")


def configure(uow, *, grant=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY, "Leitung"))
    identities.upsert_user(UserAccount(DEPUTY, "Vertretung"))
    identities.upsert_role(Role(ROLE, frozenset({PERM_KICAD_GLOBAL_SECURITY_STAFFING_RELEASE_DECIDE}) if grant else frozenset()))
    identities.upsert_role(Role(WRONG_ROLE, frozenset()))
    identities.assign_role(PRIMARY, ROLE)
    identities.assign_role(PRIMARY, WRONG_ROLE)
    identities.assign_role(DEPUTY, ROLE)
    tracked = SQLiteTrackedGlobalSecurityResponsibilityRepository(uow.connection, identities)
    tracked.assign_tracked(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Leitung"), change_id=BusinessId("GSEC-CHANGE-2001"))
    tracked.assign_tracked(GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY, DEPUTY, NOW, "Vertretung"), change_id=BusinessId("GSEC-CHANGE-2002"))
    gate = GlobalSecurityStaffingQualityGate(GlobalSecurityResponsibilityHistoryService(uow.connection, identities)).evaluate()
    releases = SQLiteGlobalSecurityStaffingReleaseRepository(uow.connection)
    attempts = SQLiteGlobalSecurityStaffingReleaseAttemptRepository(uow.connection)
    service = AuthorizedGlobalSecurityStaffingReleaseService(
        SQLiteGlobalSecurityResponsibilityRepository(uow.connection, identities), identities, releases, attempts
    )
    return service, releases, attempts, gate


def test_falsche_rolle_wird_auditiert_aber_nicht_freigegeben(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "db.sqlite") as uow:
        service, releases, attempts, gate = configure(uow)
        with pytest.raises(PermissionError, match="ERR-KICAD-0147"):
            service.decide(release_id=BusinessId("GSEC-REL-2001"), gate_result=gate, decided_at=NOW,
                           acting_role=WRONG_ROLE, reason="Falsch.", correlation_id=CorrelationId("COR-00002001"),
                           attempt_id=BusinessId("GSEC-ATT-2001"))
        record = attempts.get(BusinessId("GSEC-ATT-2001"))
        assert record.actor_id == PRIMARY
        assert record.denial_code == "ERR-KICAD-0147"
        assert releases.list_all() == ()


def test_fehlende_berechtigung_wird_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "db.sqlite") as uow:
        service, releases, attempts, gate = configure(uow, grant=False)
        with pytest.raises(PermissionError, match="ERR-KICAD-0146"):
            service.decide(release_id=BusinessId("GSEC-REL-2002"), gate_result=gate, decided_at=NOW,
                           acting_role=ROLE, reason="Ohne Recht.", correlation_id=CorrelationId("COR-00002002"),
                           attempt_id=BusinessId("GSEC-ATT-2002"))
        assert attempts.get(BusinessId("GSEC-ATT-2002")).denial_code == "ERR-KICAD-0146"
        assert releases.list_all() == ()


def test_nichtverfuegbarkeit_wird_ohne_actor_auditiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "db.sqlite") as uow:
        service, _, attempts, gate = configure(uow)
        with pytest.raises(LookupError, match="ERR-KICAD-0122"):
            service.decide(release_id=BusinessId("GSEC-REL-2003"), gate_result=gate, decided_at=NOW,
                           acting_role=ROLE, reason="Niemand da.", correlation_id=CorrelationId("COR-00002003"),
                           attempt_id=BusinessId("GSEC-ATT-2003"), unavailable_user_ids=frozenset({PRIMARY, DEPUTY}))
        record = attempts.get(BusinessId("GSEC-ATT-2003"))
        assert record.actor_id is None
        assert record.denial_code == "ERR-KICAD-0122"


def test_aktiviertes_audit_benoetigt_versuchskennung(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "db.sqlite") as uow:
        service, releases, attempts, gate = configure(uow)
        with pytest.raises(ValueError, match="ERR-KICAD-0153"):
            service.decide(release_id=BusinessId("GSEC-REL-2004"), gate_result=gate, decided_at=NOW,
                           acting_role=WRONG_ROLE, reason="Falsch.", correlation_id=CorrelationId("COR-00002004"))
        assert attempts.list_all() == ()
        assert releases.list_all() == ()
