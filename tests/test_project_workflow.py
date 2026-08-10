import json
from pathlib import Path

import pytest

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from tools.projectos_project_cli import (
    create_project,
    normalize_project_name,
    read_active_project,
    suggested_filename,
)
from tools.z_cockpit.pages import page_by_id
from tools.z_cockpit.project_access import (
    PROJECT_FILE_ADMIN,
    PROJECT_FILE_READ,
    PROJECT_FILE_SHARE,
    PROJECT_FILE_WRITE,
    PROTECTION_LEGACY_UNSPECIFIED,
    PROTECTION_PRIVATE_TEAM,
    PROTECTION_REPOSITORY_VISIBLE,
    collect_project_access,
)
from tools.z_cockpit.project_page import project_page_html
from tools.z_cockpit.user_management_page import collect_user_management, load_user_management_bundle


ROOT = Path(__file__).resolve().parents[1]


def test_create_project_uses_projectos_v4_manager_and_records_local_active_state(tmp_path):
    target = tmp_path / "Werkstatt.projectos.json"
    state_path = tmp_path / "active.json"

    created = create_project("Verteilung Werkstatt", target, state_path=state_path)

    assert target.is_file()
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["version"] == 4
    assert raw["project_id"] == created.project_id
    assert raw["user_management"]["project_id"] == created.project_id
    assert raw["user_management"]["users"] == []

    _, _, project_id, migration_required, user_management = load_projectos_bundle_details(target)
    assert project_id == created.project_id
    assert migration_required is False
    assert user_management is not None
    assert user_management.users == ()

    active = read_active_project(state_path)
    assert active == created
    active_raw = json.loads(state_path.read_text(encoding="utf-8"))
    assert active_raw["schema_version"] == 2
    assert active_raw["name"] == "Verteilung Werkstatt"
    assert active_raw["protection_mode"] == PROTECTION_PRIVATE_TEAM


def test_create_project_refuses_unconfirmed_overwrite(tmp_path):
    target = tmp_path / "existing.projectos.json"
    target.write_text("bereits vorhanden", encoding="utf-8")

    with pytest.raises(FileExistsError):
        create_project("Bestehend", target, state_path=tmp_path / "active.json")


def test_confidential_project_cannot_be_saved_inside_general_source_repository(tmp_path):
    repository_root = tmp_path / "source-repo"
    repository_root.mkdir()
    target = repository_root / "projects" / "secret.projectos.json"
    target.parent.mkdir()

    with pytest.raises(ValueError, match="Vertrauliche ProjectOS-Projekte"):
        create_project(
            "Geheim",
            target,
            state_path=tmp_path / "active.json",
            protection_mode=PROTECTION_PRIVATE_TEAM,
            repository_root=repository_root,
        )


def test_repository_visible_project_may_be_saved_inside_general_repository(tmp_path):
    repository_root = tmp_path / "source-repo"
    repository_root.mkdir()
    target = repository_root / "projects" / "shared.projectos.json"
    target.parent.mkdir()

    created = create_project(
        "Offen",
        target,
        state_path=tmp_path / "active.json",
        protection_mode=PROTECTION_REPOSITORY_VISIBLE,
        repository_root=repository_root,
    )

    assert created.protection_mode == PROTECTION_REPOSITORY_VISIBLE
    assert target.is_file()


def test_project_name_is_not_a_path_and_filename_is_deterministic():
    assert normalize_project_name("  Werkstatt 1  ") == "Werkstatt 1"
    assert suggested_filename("Werkstatt 1") == "Werkstatt 1.projectos.json"
    with pytest.raises(ValueError):
        normalize_project_name(r"C:\Projekte\Werkstatt")
    with pytest.raises(ValueError):
        normalize_project_name("../Werkstatt")


def test_stale_active_project_is_ignored(tmp_path):
    state_path = tmp_path / "active.json"
    state_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "Fehlt",
                "path": str(tmp_path / "missing.projectos.json"),
                "project_id": "10000000-0000-0000-0000-000000000001",
                "bundle_version": 4,
            }
        ),
        encoding="utf-8",
    )
    assert read_active_project(state_path) is None


def test_legacy_active_project_remains_readable_with_unspecified_protection(tmp_path):
    target = tmp_path / "legacy.projectos.json"
    created = create_project("Legacy", target, state_path=tmp_path / "new-active.json")
    state_path = tmp_path / "legacy-active.json"
    state_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "Legacy",
                "path": str(target),
                "project_id": created.project_id,
                "bundle_version": 4,
            }
        ),
        encoding="utf-8",
    )

    active = read_active_project(state_path)
    assert active is not None
    assert active.protection_mode == PROTECTION_LEGACY_UNSPECIFIED


def test_project_file_rights_are_read_from_existing_projectos_permissions():
    project_id = "10000000-0000-0000-0000-000000000001"
    user = ProjectOSUserProfile(
        user_id="20000000-0000-0000-0000-000000000001",
        display_name="Projektleitung",
    )
    state = ProjectOSUserManagementState(
        project_id=project_id,
        users=(user,),
        permission_assignments=(
            ProjectOSPermissionAssignment(
                user_id=user.user_id,
                permission=PROJECT_FILE_READ,
                source_type="direct",
                effect="allow",
            ),
            ProjectOSPermissionAssignment(
                user_id=user.user_id,
                permission=PROJECT_FILE_WRITE,
                source_type="direct",
                effect="deny",
            ),
        ),
    )
    snapshot = collect_user_management(state)

    rows = collect_project_access(snapshot)
    assert len(rows) == 1
    assert rows[0].decision_for(PROJECT_FILE_READ) == "allow"
    assert rows[0].decision_for(PROJECT_FILE_WRITE) == "deny"
    assert rows[0].decision_for(PROJECT_FILE_SHARE) == "not_granted"
    assert rows[0].decision_for(PROJECT_FILE_ADMIN) == "not_granted"


def test_project_page_offers_protected_windows_save_dialog_workflow_without_path_input():
    html = project_page_html(collect_user_management())

    assert 'id="page-projekt"' in html
    assert "ProjectOS-Projektdatei, Schutzklasse und Zugriffsrechte" in html
    assert 'id="project-new-name"' in html
    assert 'id="project-new-protection"' in html
    assert "Vertraulich · Team" in html
    assert "separates privates Projekt-Repository" in html
    assert 'id="project-new-create"' in html
    assert "projectos-z://new?name=" in html
    assert "&protection=" in html
    assert "Der Browser übergibt weiterhin keinen Dateipfad" in html
    assert "Im Simulationsmodus werden keine Projektdateien erzeugt" in html
    assert PROJECT_FILE_READ in html
    assert PROJECT_FILE_WRITE in html
    assert PROJECT_FILE_SHARE in html
    assert PROJECT_FILE_ADMIN in html
    assert 'id="project-new-path"' not in html


def test_project_page_shows_loaded_project_identity(tmp_path):
    target = tmp_path / "Werkstatt.projectos.json"
    create_project("Werkstatt", target, state_path=tmp_path / "active.json")
    snapshot = load_user_management_bundle(target)

    html = project_page_html(snapshot)

    assert "Werkstatt" in html
    assert "Werkstatt.projectos.json" in html
    assert snapshot.project_id in html
    assert "ProjectOS v4" in html
    assert "Außerhalb des allgemeinen Quell-Repositories" in html


def test_project_page_is_registered_between_start_and_devices():
    page = page_by_id("projekt")
    assert page.implemented is True
    assert page.label_de == "Projekt"


def test_windows_project_protocol_is_scoped_and_uses_domain_cli_and_protection():
    register = (ROOT / "tools" / "windows" / "register_z_project_protocol.ps1").read_text(encoding="utf-8")
    handler = (ROOT / "tools" / "windows" / "open_projectos_from_cockpit.ps1").read_text(encoding="utf-8")
    launcher = (ROOT / "tools" / "windows" / "open_z_cockpit.bat").read_text(encoding="utf-8")

    assert "HKCU:\\Software\\Classes\\projectos-z" in register
    assert "open_projectos_from_cockpit.ps1" in register
    assert "$parsed.Scheme -ne 'projectos-z'" in handler
    assert "Get-QueryValue $parsed 'name'" in handler
    assert "Get-QueryValue $parsed 'protection'" in handler
    assert "SaveFileDialog" in handler
    assert "private_team" in handler
    assert "Vertrauliche ProjectOS-Projekte dürfen nicht im allgemeinen Quell-Repository" in handler
    assert "alle Benutzer mit Leserechten auf dieses Repository sichtbar" in handler
    assert "tools.projectos_project_cli new" in handler
    assert "--output $target --protection $protection" in handler
    assert "Get-QueryValue $parsed 'path'" not in handler
    assert "register_z_project_protocol.ps1" in launcher
    assert "tools.projectos_project_cli active --path-only" in launcher
    assert "tools.generate_z_cockpit --project-bundle" in launcher
