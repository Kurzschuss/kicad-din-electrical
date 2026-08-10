from datetime import datetime, timezone

import pytest

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_user_management_persistence import ProjectOSUserManagementState
from tools.z_cockpit.user_management_page import collect_user_management
from tools.z_cockpit.user_simulation import (
    TEST_USER_ID,
    collect_identity_users,
    simulation_test_user,
    user_simulation_html,
)


PROJECT_ID = "10000000-0000-0000-0000-000000000001"
USER_ID = "20000000-0000-0000-0000-000000000001"
AT = datetime(2026, 8, 10, 20, 0, tzinfo=timezone.utc)


def snapshot(display_name: str = "Uwe Test"):
    user = ProjectOSUserProfile(
        user_id=USER_ID,
        display_name=display_name,
        weight=250,
        roles=("maintainer",),
    )
    state = ProjectOSUserManagementState(
        project_id=PROJECT_ID,
        users=(user,),
        permission_assignments=(
            ProjectOSPermissionAssignment(
                user_id=USER_ID,
                permission="devices.read",
                source_type="direct",
                effect="allow",
            ),
            ProjectOSPermissionAssignment(
                user_id=USER_ID,
                permission="settings.write",
                source_type="deny",
                effect="deny",
                risk_class="high",
            ),
        ),
    )
    return collect_user_management(state, source_label="test.projectos", at=AT)


def test_identity_collection_uses_resolved_projectos_rights_and_adds_test_user():
    users = collect_identity_users(snapshot())

    assert len(users) == 2
    real = next(item for item in users if item.user_id == USER_ID)
    test = next(item for item in users if item.user_id == TEST_USER_ID)

    assert real.display_name == "Uwe Test"
    assert real.weight == 250
    assert real.roles == ("maintainer",)
    assert real.allowed_count == 1
    assert real.denied_count == 1
    assert ("devices.read", "Erlaubt") in real.permissions
    assert ("settings.write", "Verweigert") in real.permissions

    assert test.display_name == "Testuser"
    assert test.status_label == "Aktiv"
    assert test.weight == 100
    assert test.roles == ("Testbenutzer",)
    assert test.permissions == ()
    assert test.simulation_only is True


def test_test_user_weight_is_local_and_validated():
    assert simulation_test_user(weight=0).weight == 0
    assert simulation_test_user(weight=1000).weight == 1000
    with pytest.raises(ValueError):
        simulation_test_user(weight=-1)
    with pytest.raises(ValueError):
        simulation_test_user(weight=1001)


def test_simulation_ui_contains_identity_bar_testuser_and_read_only_controls():
    html = user_simulation_html(snapshot())

    assert "Aktive ProjectOS-Identität" in html
    assert "Bearbeitungsstatus" in html
    assert "Gewichtung" in html
    assert "Rollen" in html
    assert "Simulationsmodus" in html
    assert "Testuser" in html
    assert TEST_USER_ID in html
    assert "z-cockpit.identity.v1" in html
    assert "keine Anmeldung" in html
    assert "verändert keine ProjectOS-Daten" in html
    assert "kicad-z:" in html
    assert "Editoraufruf blockiert" in html
    assert "Die Gewichtung beeinflusst die Rechteentscheidung nicht" in html


def test_simulation_payload_cannot_close_its_script_tag():
    html = user_simulation_html(snapshot('</script><script>alert("x")</script>'))

    assert '</script><script>alert("x")</script>' not in html
    assert '<\\/script><script>alert' in html
