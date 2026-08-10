import json
from pathlib import Path

import pytest

from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from tools.projectos_project_cli import (
    create_project,
    normalize_project_name,
    read_active_project,
    suggested_filename,
)
from tools.z_cockpit.pages import page_by_id
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
    assert json.loads(state_path.read_text(encoding="utf-8"))["name"] == "Verteilung Werkstatt"


def test_create_project_refuses_unconfirmed_overwrite(tmp_path):
    target = tmp_path / "existing.projectos.json"
    target.write_text("bereits vorhanden", encoding="utf-8")

    with pytest.raises(FileExistsError):
        create_project("Bestehend", target, state_path=tmp_path / "active.json")


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


def test_project_page_offers_windows_save_dialog_workflow_without_path_input():
    html = project_page_html(collect_user_management())

    assert 'id="page-projekt"' in html
    assert "ProjectOS-Projektdatei erstellen und aktives Projekt verwalten" in html
    assert 'id="project-new-name"' in html
    assert 'id="project-new-create"' in html
    assert "projectos-z://new?name=" in html
    assert "Der Browser übergibt keinen Dateipfad" in html
    assert "Im Simulationsmodus werden keine Projektdateien erzeugt" in html
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


def test_project_page_is_registered_between_start_and_devices():
    page = page_by_id("projekt")
    assert page.implemented is True
    assert page.label_de == "Projekt"


def test_windows_project_protocol_is_scoped_and_uses_domain_cli():
    register = (ROOT / "tools" / "windows" / "register_z_project_protocol.ps1").read_text(encoding="utf-8")
    handler = (ROOT / "tools" / "windows" / "open_projectos_from_cockpit.ps1").read_text(encoding="utf-8")
    launcher = (ROOT / "tools" / "windows" / "open_z_cockpit.bat").read_text(encoding="utf-8")

    assert "HKCU:\\Software\\Classes\\projectos-z" in register
    assert "open_projectos_from_cockpit.ps1" in register
    assert "$parsed.Scheme -ne 'projectos-z'" in handler
    assert "Get-QueryValue $parsed 'name'" in handler
    assert "SaveFileDialog" in handler
    assert "tools.projectos_project_cli new" in handler
    assert "--output $target" in handler
    assert "Get-QueryValue $parsed 'path'" not in handler
    assert "register_z_project_protocol.ps1" in launcher
    assert "tools.projectos_project_cli active --path-only" in launcher
    assert "tools.generate_z_cockpit --project-bundle" in launcher
