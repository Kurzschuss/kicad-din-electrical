from datetime import datetime, timedelta, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_user_project_roles import ZCockpitUserProjectRoleView


def test_active_project_role_and_derived_permission_are_visible():
    project_id = str(uuid4())
    assigner_id = str(uuid4())
    user = ProjectOSUserProfile("Uwe", weight=850)
    role = ProjectOSUserProjectRole(
        project_id=project_id,
        user_id=user.user_id,
        role_type="project_lead",
        assigned_by_user_id=assigner_id,
    )
    view = ZCockpitUserProjectRoleView(
        project_id=project_id,
        user=user,
        roles=[role],
        permission_map={"project_lead": ["project.release"]},
    )

    state = view.state()

    assert state["active_roles"][0]["role_label"] == "Projektleiter"
    assert state["active_roles"][0]["assigned_by_user_id"] == assigner_id
    assert state["permissions"][0]["decision"] == "allow"
    assert state["permissions"][0]["sources"][0]["metadata"]["project_role"] == "project_lead"
    assert state["weight"] == 850
    assert state["weight_used_for_decision"] is False


def test_expired_project_role_is_visible_but_does_not_grant_permission():
    now = datetime.now(timezone.utc)
    user = ProjectOSUserProfile("User")
    role = ProjectOSUserProjectRole(
        project_id=str(uuid4()),
        user_id=user.user_id,
        role_type="deputy",
        valid_until=(now - timedelta(hours=1)).isoformat(),
    )
    view = ZCockpitUserProjectRoleView(
        project_id=role.project_id,
        user=user,
        roles=[role],
        permission_map={"deputy": ["project.edit"]},
    )

    state = view.state(at=now)

    assert state["active_roles"] == []
    assert state["inactive_roles"][0]["role_label"] == "Stellvertretung"
    assert state["permissions"] == []


def test_explicit_deny_still_overrides_project_role_allow():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User", weight=999)
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="project_lead")
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
    )
    view = ZCockpitUserProjectRoleView(
        project_id=project_id,
        user=user,
        roles=[role],
        base_assignments=[deny],
        permission_map={"project_lead": ["project.release"]},
    )

    state = view.state()

    assert state["permissions"][0]["decision"] == "deny"
    assert state["permissions"][0]["deny_precedence"] is True
    assert state["permissions"][0]["weight_used_for_decision"] is False


def test_role_simulation_is_read_only_and_shows_decision_change():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User")
    view = ZCockpitUserProjectRoleView(
        project_id=project_id,
        user=user,
        permission_map={"trusted_person": ["project.review"]},
    )
    hypothetical = ProjectOSUserProjectRole(
        project_id=project_id,
        user_id=user.user_id,
        role_type="trusted_person",
    )

    result = view.simulate_roles(hypothetical_roles=[hypothetical], permission="project.review")

    assert result["baseline"]["decision"] == "not_granted"
    assert result["simulated"]["decision"] == "allow"
    assert result["decision_changed"] is True
    assert result["read_only"] is True
    assert view.state()["active_roles"] == []
