from datetime import datetime, timezone

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_user_deactivation import ProjectOSUserDeactivation
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from tools.z_cockpit.user_management_page import (
    collect_user_management,
    user_management_page_html,
)


PROJECT_ID = "10000000-0000-0000-0000-000000000001"
ADMIN_ID = "20000000-0000-0000-0000-000000000001"
TECH_ID = "20000000-0000-0000-0000-000000000002"
AT = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)


def sample_state() -> ProjectOSUserManagementState:
    admin = ProjectOSUserProfile(
        user_id=ADMIN_ID,
        display_name="Projektleitung",
        roles=("maintainer",),
    )
    tech = ProjectOSUserProfile(
        user_id=TECH_ID,
        display_name="Technik",
    )
    return ProjectOSUserManagementState(
        project_id=PROJECT_ID,
        users=(admin, tech),
        user_deactivations=(
            ProjectOSUserDeactivation(
                project_id=PROJECT_ID,
                user_id=TECH_ID,
                deactivated_at="2026-08-09T10:00:00+00:00",
                deactivated_by_user_id=ADMIN_ID,
                reason="Projektzugriff vorübergehend beendet",
            ),
        ),
        permission_assignments=(
            ProjectOSPermissionAssignment(
                user_id=ADMIN_ID,
                permission="users.manage",
                source_type="direct",
                effect="allow",
                risk_class="high",
            ),
            ProjectOSPermissionAssignment(
                user_id=ADMIN_ID,
                permission="settings.write",
                source_type="deny",
                effect="deny",
                risk_class="critical",
            ),
            ProjectOSPermissionAssignment(
                user_id=TECH_ID,
                permission="devices.read",
                source_type="direct",
                effect="allow",
            ),
        ),
        project_roles=(
            ProjectOSUserProjectRole(
                project_id=PROJECT_ID,
                user_id=ADMIN_ID,
                role_type="project_lead",
                assigned_by_user_id=ADMIN_ID,
            ),
        ),
    )


def test_collect_user_management_uses_existing_projectos_state():
    snapshot = collect_user_management(sample_state(), source_label="test.projectos", at=AT)

    assert snapshot.project_id == PROJECT_ID
    assert snapshot.source_available is True
    assert snapshot.source_label == "test.projectos"
    assert snapshot.active_count == 1
    assert snapshot.deactivated_count == 1
    assert len(snapshot.users) == 2

    admin = next(item for item in snapshot.users if item.user_id == ADMIN_ID)
    tech = next(item for item in snapshot.users if item.user_id == TECH_ID)

    assert admin.status_label == "Aktiv"
    assert "maintainer" in admin.roles
    assert "Projektleiter" in admin.roles
    assert admin.allowed_count == 1
    assert admin.denied_count == 1
    assert {item.permission for item in admin.permissions} == {"users.manage", "settings.write"}
    assert next(item for item in admin.permissions if item.permission == "users.manage").sources == (
        "Direkte Zuweisung",
    )

    assert tech.status_label == "Deaktiviert"
    assert tech.denied_count == 1
    permission = tech.permissions[0]
    assert permission.permission == "devices.read"
    assert permission.decision == "user_deactivated"
    assert permission.decision_label == "Benutzer deaktiviert"
    assert len(tech.lifecycle_events) == 1


def test_user_management_page_uses_compact_heading_filters_table_and_fixed_inspector():
    html = user_management_page_html(
        collect_user_management(sample_state(), source_label="test.projectos", at=AT)
    )

    assert 'id="page-benutzer"' in html
    assert 'class="cockpit-page-title">Benutzerverwaltung ' in html
    assert "(ProjectOS-Benutzer, Lifecycle, Rollen und effektive Rechte.)" in html
    assert 'id="user-management-filter-search"' in html
    assert 'id="user-management-filter-status"' in html
    assert 'id="user-management-filter-role"' in html
    assert 'id="user-management-filter-permission"' in html
    assert 'id="user-management-overview"' in html
    assert 'class="user-management-inspector"' in html
    assert "Projektleitung" in html
    assert ADMIN_ID in html
    assert "Projektleiter" in html
    assert "users.manage" in html
    assert "Direkte Zuweisung" in html
    assert "Projektzugriff vorübergehend beendet" in html
    assert "Schreibende Aktionen werden erst über die bestehenden autorisierten ProjectOS-Services angebunden" in html


def test_empty_user_management_page_does_not_invent_users():
    snapshot = collect_user_management(at=AT)
    html = user_management_page_html(snapshot)

    assert snapshot.source_available is False
    assert snapshot.users == ()
    assert "Keine ProjectOS-Benutzer geladen" in html
    assert "--project-bundle" in html
    assert "Keine ProjectOS-Projektdatei angebunden" in html


def test_user_management_page_escapes_user_controlled_values():
    user = ProjectOSUserProfile(
        user_id=ADMIN_ID,
        display_name="<script>alert(1)</script>",
        roles=("<Admin>",),
    )
    state = ProjectOSUserManagementState(project_id=PROJECT_ID, users=(user,))
    html = user_management_page_html(
        collect_user_management(state, source_label="<projekt>", at=AT)
    )

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;Admin&gt;" in html
    assert "&lt;projekt&gt;" in html
