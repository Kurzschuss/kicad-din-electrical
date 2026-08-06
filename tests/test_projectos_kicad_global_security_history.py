from datetime import datetime, timedelta, timezone

import pytest

from projectos import (
    BusinessId,
    GlobalSecurityResponsibility,
    GlobalSecurityResponsibilityHistoryService,
    GlobalSecurityResponsibilitySearchFilter,
    GlobalSecurityResponsibilityType,
    SQLiteIdentityRepository,
    SQLiteTrackedGlobalSecurityResponsibilityRepository,
    SQLiteUnitOfWork,
    UserAccount,
)

NOW = datetime(2026, 8, 6, 15, 0, tzinfo=timezone.utc)
PRIMARY = BusinessId("USR-SECURITY")
DEPUTY = BusinessId("USR-DEPUTY")
NEW_PRIMARY = BusinessId("USR-NEW-SECURITY")


def configure(uow):
    identities = SQLiteIdentityRepository(uow.connection)
    for user_id, name in (
        (PRIMARY, "Sicherheit"), (DEPUTY, "Stellvertretung"), (NEW_PRIMARY, "Neue Sicherheit")
    ):
        identities.upsert_user(UserAccount(user_id, name))
    repository = SQLiteTrackedGlobalSecurityResponsibilityRepository(uow.connection, identities)
    service = GlobalSecurityResponsibilityHistoryService(uow.connection, identities)
    return identities, repository, service


def test_zuweisungen_werden_mit_vorgaenger_historisiert(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        _, repository, service = configure(uow)
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Erstzuweisung"),
            change_id=BusinessId("GSEC-CHANGE-0001"),
        )
        second = repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, NEW_PRIMARY, NOW + timedelta(hours=1), "Wechsel"),
            change_id=BusinessId("GSEC-CHANGE-0002"),
        )
        assert second.previous_user_id == PRIMARY
        page = service.search(page_size=10)
        assert page.total_items == 2
        assert page.items[0].user_id == NEW_PRIMARY


def test_suche_filtert_typ_benutzer_und_zeitraum(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        _, repository, service = configure(uow)
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Primär"),
            change_id=BusinessId("GSEC-CHANGE-0010"),
        )
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY, DEPUTY, NOW + timedelta(minutes=5), "Vertretung"),
            change_id=BusinessId("GSEC-CHANGE-0011"),
        )
        result = service.search(GlobalSecurityResponsibilitySearchFilter(
            responsibility=GlobalSecurityResponsibilityType.DEPUTY,
            user_id=DEPUTY,
            from_timestamp=NOW + timedelta(minutes=1),
            until_timestamp=NOW + timedelta(minutes=10),
        ))
        assert result.total_items == 1
        assert result.items[0].responsibility is GlobalSecurityResponsibilityType.DEPUTY


def test_diagnose_erkennt_vollstaendige_getrennte_verantwortung(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        _, repository, service = configure(uow)
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Primär"),
            change_id=BusinessId("GSEC-CHANGE-0020"),
        )
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY, DEPUTY, NOW, "Vertretung"),
            change_id=BusinessId("GSEC-CHANGE-0021"),
        )
        diagnostic = service.diagnostic()
        assert diagnostic.complete
        assert not diagnostic.same_user_assigned_twice
        assert diagnostic.total_changes == 2


def test_diagnose_erkennt_dieselbe_person_in_beiden_funktionen(tmp_path):
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        _, repository, service = configure(uow)
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Primär"),
            change_id=BusinessId("GSEC-CHANGE-0030"),
        )
        repository.assign_tracked(
            GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.DEPUTY, PRIMARY, NOW, "Unzulängliche Vertretung"),
            change_id=BusinessId("GSEC-CHANGE-0031"),
        )
        diagnostic = service.diagnostic()
        assert diagnostic.same_user_assigned_twice
        assert not diagnostic.complete


def test_parameter_und_doppelte_wechselkennung_werden_abgelehnt(tmp_path):
    with pytest.raises(ValueError, match="ERR-KICAD-0129"):
        GlobalSecurityResponsibilitySearchFilter(from_timestamp=datetime(2026, 8, 6))
    with SQLiteUnitOfWork(tmp_path / "projectos.db") as uow:
        _, repository, service = configure(uow)
        value = GlobalSecurityResponsibility(GlobalSecurityResponsibilityType.PRIMARY, PRIMARY, NOW, "Primär")
        repository.assign_tracked(value, change_id=BusinessId("GSEC-CHANGE-0040"))
        with pytest.raises(ValueError, match="ERR-KICAD-0131"):
            repository.assign_tracked(value, change_id=BusinessId("GSEC-CHANGE-0040"))
        with pytest.raises(ValueError, match="ERR-KICAD-0133"):
            service.search(page=0)
