from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_role_transition import ZCockpitProjectRoleTransitionView


def test_project_lead_view_shows_gained_permission_and_risk():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Uwe", weight=850)
    deputy = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    view = ZCockpitProjectRoleTransitionView(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ("project.edit",)},
    )

    state = view.simulate(add_roles=(deputy,), at=datetime(2026, 8, 9, tzinfo=timezone.utc))

    assert state["gained_permissions"] == ["project.edit"]
    assert state["lost_permissions"] == []
    assert state["simulated_roles"][0]["role_label"] == "Stellvertretung"
    assert state["read_only"] is True


def test_project_lead_view_shows_removed_permission():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Uwe")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="project_lead")
    view = ZCockpitProjectRoleTransitionView(
        project_id=project_id,
        user=user,
        roles=(role,),
        permission_map={"project_lead": ("project.release",)},
    )

    state = view.simulate(
        remove_role_assignment_ids=(role.role_assignment_id,),
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )

    assert state["lost_permissions"] == ["project.release"]
    assert state["changed_permission_count"] == 1


def test_project_lead_view_reports_deny_conflict_after_role_addition():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Uwe", weight=900)
    deputy = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
        risk_class="critical",
    )
    view = ZCockpitProjectRoleTransitionView(
        project_id=project_id,
        user=user,
        base_assignments=(deny,),
        permission_map={"deputy": ("project.release",)},
    )

    state = view.simulate(add_roles=(deputy,), at=datetime(2026, 8, 9, tzinfo=timezone.utc))

    assert state["gained_permissions"] == []
    assert state["deny_conflict_count"] == 1
    assert state["deny_conflicts"][0]["permission"] == "project.release"
    assert state["deny_conflicts"][0]["after"]["decision"] == "deny"
    assert state["user"]["weight"] == 900


def test_project_lead_view_reports_no_effect_without_permission_change():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Uwe")
    trusted = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="trusted_person")
    view = ZCockpitProjectRoleTransitionView(
        project_id=project_id,
        user=user,
        permission_map={"trusted_person": ()},
    )

    state = view.simulate(add_roles=(trusted,), at=datetime(2026, 8, 9, tzinfo=timezone.utc))

    assert state["changed_permission_count"] == 0
    assert state["summary"] == "Der simulierte Funktionswechsel verändert keine effektive Rechteentscheidung."
