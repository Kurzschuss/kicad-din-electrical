from datetime import datetime, timezone

import pytest

from projectos import (
    BusinessId,
    GlobalSecurityResponsibility,
    GlobalSecurityResponsibilityHistoryService,
    GlobalSecurityResponsibilityType,
    GlobalSecurityStaffingDecision,
    GlobalSecurityStaffingPolicy,
    GlobalSecurityStaffingQualityGate,
    SQLiteIdentityRepository,
    SQLiteTrackedGlobalSecurityResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 15, 0, tzinfo=timezone.utc)
PRIMARY = BusinessId("USR-SECURITY")
DEPUTY = BusinessId("USR-SECURITY-DEPUTY")


def setup_gate(uow, *, primary=True, deputy=True, same=False, active_primary=True, active_deputy=True):
    identities = SQLiteIdentityRepository(uow.connection)
    identities.upsert_user(UserAccount(PRIMARY, "Sicherheitsleitung", active_primary))
    identities.upsert_user(UserAccount(DEPUTY, "Sicherheitsvertretung", active_deputy))
    tracked = SQLiteTrackedGlobalSecurityResponsibilityRepository(uow.connection, identities)
    if primary:
        tracked.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Hauptverantwortung"),
            change_id=BusinessId("GSEC-CHANGE-0001"),
        )
    if deputy:
        tracked.assign_tracked(
            GlobalSecurityResponsibility(
                GlobalSecurityResponsibilityType.DEPUTY,
                PRIMARY if same else DEPUTY,
                NOW,
                "Stellvertretung",
            ),
            change_id=BusinessId("GSEC-CHANGE-0002"),
        )
    history = GlobalSecurityResponsibilityHistoryService(uow.connection, identities)
    return GlobalSecurityStaffingQualityGate(history)


def test_vollstaendige_getrennte_besetzung_wird_freigegeben(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow).evaluate()
        assert result.decision is GlobalSecurityStaffingDecision.APPROVED
        assert result.findings == ()


def test_fehlende_stellvertretung_wird_abgelehnt(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow, deputy=False).evaluate()
        assert result.decision is GlobalSecurityStaffingDecision.REJECTED
        assert [item.code for item in result.findings] == ["ERR-KICAD-0138"]


def test_inaktive_hauptverantwortung_wird_abgelehnt(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow, active_primary=False).evaluate()
        assert result.decision is GlobalSecurityStaffingDecision.REJECTED
        assert "ERR-KICAD-0139" in {item.code for item in result.findings}


def test_doppelbesetzung_wird_abgelehnt(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow, same=True).evaluate()
        assert result.decision is GlobalSecurityStaffingDecision.REJECTED
        assert "ERR-KICAD-0141" in {item.code for item in result.findings}


def test_unzureichende_historie_ist_eigene_entscheidung(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow).evaluate(GlobalSecurityStaffingPolicy(minimum_history_entries=3))
        assert result.decision is GlobalSecurityStaffingDecision.INSUFFICIENT_DATA
        assert result.findings[0].code == "ERR-KICAD-0136"


def test_richtlinie_kann_stellvertretung_optional_machen(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        result = setup_gate(uow, deputy=False).evaluate(GlobalSecurityStaffingPolicy(
            require_deputy=False,
            require_active_deputy=False,
        ))
        assert result.decision is GlobalSecurityStaffingDecision.APPROVED


def test_negative_mindesthistorie_wird_abgelehnt():
    with pytest.raises(ValueError, match="ERR-KICAD-0135"):
        GlobalSecurityStaffingPolicy(minimum_history_entries=-1)
