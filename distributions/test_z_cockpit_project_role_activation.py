from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_project_role_activation import ZCockpitProjectRoleActivationView


def _now():
    return datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)


def test_assigned_role_without_activation_has_no_rights():
    user = ProjectOSUserProfile("Uwe", weight=900)
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    view = ZCockpitProjectRoleActivationView(
        project_id=project_id,
        user=user,
        roles=(role,),
        permission_map={"deputy": ("project.release",)},
    )
    state = view.state(at=_now())
    assert state["active_roles"] == []
    assert state["assigned_not_activated_roles"][0]["role_label"] == "Stellvertretung"
    assert state["rights"] == []


def test_active_activation_adds_role_right_and_keeps_origin_visible():
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="vacation",
        triggered_by_user_id=str(uuid4()),
        trigger_reference="absence:42",
    )
    view = ZCockpitProjectRoleActivationView(
        project_id=project_id,
        user=user,
        roles=(role,),
        activations=(activation,),
        permission_map={"deputy": ("project.release",)},
    )
    state = view.state(at=_now())
    assert state["active_roles"][0]["activation"]["reason_label"] == "Urlaub"
    assert state["rights"][0]["allowed"] is True
    source = state["rights"][0]["sources"][0]
    assert source["metadata"]["activation_id"] == activation.activation_id
    assert source["metadata"]["activation_reason"] == "vacation"


def test_simulation_shows_new_right_without_mutating_baseline():
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="successor")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="succession",
    )
    view = ZCockpitProjectRoleActivationView(
        project_id=project_id,
        user=user,
        roles=(role,),
        permission_map={"successor": ("project.manage",)},
    )
    simulation = view.simulate_activation(activation, at=_now())
    impact = simulation["permission_impacts"][0]
    assert simulation["before"]["rights"] == []
    assert impact["became_allowed"] is True
    assert simulation["after"]["active_roles"][0]["role_label"] == "Nachfolger"
    assert view.state(at=_now())["rights"] == []


def test_simulation_marks_deny_conflict():
    user = ProjectOSUserProfile("Uwe", weight=1000)
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="emergency",
    )
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
        risk_class="critical",
    )
    view = ZCockpitProjectRoleActivationView(
        project_id=project_id,
        user=user,
        roles=(role,),
        base_assignments=(deny,),
        permission_map={"deputy": ("project.release",)},
    )
    simulation = view.simulate_activation(activation, at=_now())
    impact = simulation["permission_impacts"][0]
    assert impact["deny_conflict"] is True
    assert impact["after"]["decision"] == "deny"
    assert impact["after"]["weight_used_for_decision"] is False
