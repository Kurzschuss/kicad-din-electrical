from __future__ import annotations

import json

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator, ProjectOSUserProfile
from distributions.projectos_project_bundle_v4 import load_projectos_bundle_details
from distributions.projectos_user_management_persistence import (
    ProjectOSUserManagementState,
    USER_MANAGEMENT_PERSISTENCE_VERSION,
)
from tools.projectos_governance import (
    add_access_rule,
    bootstrap_admin,
    create_user,
    update_user,
)
from tools.projectos_project_cli import create_project
from tools.z_cockpit.governance_controls import governance_controls_html
from tools.z_cockpit.permissions_page import load_permissions_bundle
from tools.z_cockpit.user_management_page import load_user_management_bundle


def test_user_profile_persists_unique_github_login():
    user = ProjectOSUserProfile(
        display_name="Uwe Z.",
        weight=275,
        github_login="Kurzschuss",
    )
    state = ProjectOSUserManagementState(
        project_id="10000000-0000-0000-0000-000000000001",
        users=(user,),
    )
    payload = state.as_dict()
    assert payload["version"] == USER_MANAGEMENT_PERSISTENCE_VERSION == 5
    assert payload["users"][0]["github_login"] == "Kurzschuss"
    restored = ProjectOSUserManagementState.from_dict(payload)
    assert restored.users[0].github_login == "Kurzschuss"


def test_legacy_v4_user_management_without_github_login_still_loads():
    payload = {
        "version": 4,
        "project_id": "10000000-0000-0000-0000-000000000001",
        "users": [{
            "user_id": "20000000-0000-0000-0000-000000000001",
            "display_name": "Altbenutzer",
            "weight": 100,
            "roles": [],
        }],
    }
    restored = ProjectOSUserManagementState.from_dict(payload)
    assert restored.users[0].github_login is None


def test_bootstrap_user_management_and_white_blacklist_are_persisted(tmp_path, monkeypatch):
    target = tmp_path / "Team.projectos.json"
    create_project("Team", target, state_path=tmp_path / "active.json")

    monkeypatch.setattr("tools.projectos_governance._repository_write_gate", lambda: None)
    monkeypatch.setattr("tools.projectos_governance.authenticated_github_user", lambda: "Kurzschuss")
    monkeypatch.setattr("tools.projectos_governance.load_authorized_developers", lambda: {"kurzschuss"})

    admin = bootstrap_admin(target, display_name="Projektleitung")
    assert admin["github_login"] == "Kurzschuss"

    created = create_user(target, display_name="Prüfer", weight=250, github_login="Pruefer-1")
    user_id = created["user"]["user_id"]
    updated = update_user(
        target,
        user_id=user_id,
        display_name="Prüfer Elektro",
        weight=300,
        github_login="Pruefer-1",
    )
    assert updated["user"]["display_name"] == "Prüfer Elektro"
    assert updated["user"]["weight"] == 300

    allow = add_access_rule(
        target,
        user_id=user_id,
        permission="cockpit.view",
        scope="page:diagnose",
        list_type="whitelist",
    )
    deny = add_access_rule(
        target,
        user_id=user_id,
        permission="cockpit.view",
        scope="page:diagnose",
        list_type="blacklist",
    )
    assert allow["assignment"]["source_type"] == "whitelist"
    assert deny["assignment"]["source_type"] == "blacklist"

    _, _, _, _, state = load_projectos_bundle_details(target)
    assert state is not None
    user = next(item for item in state.users if item.user_id == user_id)
    decision = ProjectOSAuthorizationEvaluator(
        state.permission_assignments,
        state.permission_revocations,
        state.user_deactivations,
        state.user_reactivations,
    ).evaluate(user, "cockpit.view", scope="page:diagnose")
    assert decision["decision"] == "deny"
    assert decision["allowed"] is False


def test_governance_controls_show_user_weight_access_and_reporting_right(tmp_path):
    target = tmp_path / "Cockpit.projectos.json"
    create_project("Cockpit", target, state_path=tmp_path / "active.json")
    users = load_user_management_bundle(target)
    permissions = load_permissions_bundle(target)
    html = governance_controls_html(users, permissions)
    assert "Benutzerverwaltung &amp; Zugriffsstatus" in html
    assert "Gewichtung (0–1000)" in html
    assert "White-/Blacklist &amp; Zugriffsregeln verwalten" in html
    assert "github.issue.auto_submit" in html
    assert "page:fehlerbericht" in html
    assert "projectos-z://governance" in html
    assert "projectos-z://report?mode=auto" in html
