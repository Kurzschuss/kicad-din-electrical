import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_permission_revocation import ProjectOSPermissionRevocation
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from tools.z_cockpit.permissions_page import (
    collect_permissions,
    load_repository_developer_whitelist,
    permissions_page_html,
)


PROJECT_ID = "00000000-0000-0000-0000-000000000001"
USER_ID = "00000000-0000-0000-0000-000000000002"
ASSIGNER_ID = "00000000-0000-0000-0000-000000000003"
WHITELIST_ID = "00000000-0000-0000-0000-000000000010"
BLACKLIST_ID = "00000000-0000-0000-0000-000000000011"
EXCEPTION_ID = "00000000-0000-0000-0000-000000000012"
REVOKED_ID = "00000000-0000-0000-0000-000000000013"


def sample_state() -> ProjectOSUserManagementState:
    user = ProjectOSUserProfile(user_id=USER_ID, display_name="Max Mustermann")
    assigner = ProjectOSUserProfile(user_id=ASSIGNER_ID, display_name="Projektleitung")
    whitelist = ProjectOSPermissionAssignment(
        assignment_id=WHITELIST_ID,
        user_id=USER_ID,
        permission="device.write",
        source_type="whitelist",
        effect="allow",
        risk_class="medium",
        source_reference="test:whitelist",
    )
    blacklist = ProjectOSPermissionAssignment(
        assignment_id=BLACKLIST_ID,
        user_id=USER_ID,
        permission="device.write",
        source_type="blacklist",
        effect="deny",
        risk_class="high",
        source_reference="test:blacklist",
    )
    exception = ProjectOSPermissionAssignment(
        assignment_id=EXCEPTION_ID,
        user_id=USER_ID,
        permission="release.preview",
        source_type="exception",
        effect="allow",
        valid_until="2026-08-11T00:00:00+00:00",
    )
    revoked = ProjectOSPermissionAssignment(
        assignment_id=REVOKED_ID,
        user_id=USER_ID,
        permission="legacy.read",
        source_type="direct",
        effect="allow",
    )
    revocation = ProjectOSPermissionRevocation(
        assignment_id=REVOKED_ID,
        project_id=PROJECT_ID,
        user_id=USER_ID,
        scope="project",
        revoked_at="2026-08-09T00:00:00+00:00",
        revoked_by_user_id=ASSIGNER_ID,
        reason="Altfreigabe entfernt",
    )
    return ProjectOSUserManagementState(
        project_id=PROJECT_ID,
        users=(user, assigner),
        permission_assignments=(whitelist, blacklist, exception, revoked),
        permission_revocations=(revocation,),
    )


def write_developer_whitelist(path: Path) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "github_users": ["Kurzschuss", "Reviewer"]}),
        encoding="utf-8",
    )


def test_collect_permissions_keeps_whitelist_blacklist_and_exceptions_separate(tmp_path: Path):
    developer_path = tmp_path / "authorized_developers.json"
    write_developer_whitelist(developer_path)
    snapshot = collect_permissions(
        sample_state(),
        at=datetime(2026, 8, 10, 12, tzinfo=timezone.utc),
        developer_whitelist_path=developer_path,
    )
    assert snapshot.source_available is True
    assert snapshot.whitelist_count == 1
    assert snapshot.blacklist_count == 1
    assert snapshot.exception_count == 1
    assert snapshot.developer_whitelist.github_users == ("Kurzschuss", "Reviewer")

    whitelist = next(item for item in snapshot.assignments if item.assignment_id == WHITELIST_ID)
    assert whitelist.source_label == "Whitelist"
    assert whitelist.status_label == "Aktiv"
    assert whitelist.effective_decision_label == "Verweigert"
    assert "Blacklist" in whitelist.effective_sources

    revoked = next(item for item in snapshot.assignments if item.assignment_id == REVOKED_ID)
    assert revoked.status_label == "Widerrufen"
    assert revoked.effective_decision_label == "Nicht erteilt"


def test_developer_whitelist_is_repository_source_and_validated(tmp_path: Path):
    path = tmp_path / "authorized_developers.json"
    write_developer_whitelist(path)
    result = load_repository_developer_whitelist(path)
    assert result.available is True
    assert result.schema_version == 1
    assert result.github_users == ("Kurzschuss", "Reviewer")

    path.write_text('{"schema_version":2,"github_users":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="schema_version"):
        load_repository_developer_whitelist(path)


def test_permissions_page_shows_strict_separation_and_controlled_change_paths(tmp_path: Path):
    developer_path = tmp_path / "authorized_developers.json"
    write_developer_whitelist(developer_path)
    snapshot = collect_permissions(
        sample_state(),
        at=datetime(2026, 8, 10, 12, tzinfo=timezone.utc),
        developer_whitelist_path=developer_path,
    )
    html = permissions_page_html(snapshot)
    assert 'id="page-berechtigungen"' in html
    assert 'id="permissions-overview"' in html
    assert 'id="permissions-filter-user"' in html
    assert 'id="permissions-filter-source"' in html
    assert 'id="permissions-filter-effect"' in html
    assert 'id="permissions-filter-status"' in html
    assert "ProjectOS-Whitelist, Blacklist und Ausnahmen" in html
    assert "Repository-Entwickler-Whitelist" in html
    assert "config/authorized_developers.json" in html
    assert "ProjectOSUserManagementChangeService" in html
    assert "fail-closed Command-Autorisierung" in html
    assert "Das statische Cockpit schreibt keine Rechte" in html
    assert "DENY/Blacklist" in html
    assert "Kurzschuss" in html
    assert "Reviewer" in html


def test_permissions_page_escapes_project_data(tmp_path: Path):
    developer_path = tmp_path / "authorized_developers.json"
    developer_path.write_text(
        json.dumps({"schema_version": 1, "github_users": ["<admin>"]}), encoding="utf-8"
    )
    user = ProjectOSUserProfile(user_id=USER_ID, display_name="<script>alert(1)</script>")
    assignment = ProjectOSPermissionAssignment(
        user_id=USER_ID,
        permission="danger<write>",
        source_type="whitelist",
        effect="allow",
    )
    state = ProjectOSUserManagementState(
        project_id=PROJECT_ID,
        users=(user,),
        permission_assignments=(assignment,),
    )
    html = permissions_page_html(
        collect_permissions(state, developer_whitelist_path=developer_path)
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "danger&lt;write&gt;" in html
    assert "&lt;admin&gt;" in html
