from uuid import uuid4

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_transition import ProjectOSProjectRoleTransitionSimulator
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole


def test_add_deputy_grants_mapped_permission_read_only():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User")
    deputy = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    simulator = ProjectOSProjectRoleTransitionSimulator(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.edit"]},
    )

    result = simulator.simulate(add_roles=[deputy], permissions=["project.edit"])

    impact = result["permission_impacts"][0]
    assert impact["before"]["decision"] == "not_granted"
    assert impact["after"]["decision"] == "allow"
    assert impact["became_allowed"] is True
    assert result["changed_permission_count"] == 1
    assert result["read_only"] is True


def test_remove_project_lead_revokes_only_role_derived_permission():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User")
    lead = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="project_lead")
    simulator = ProjectOSProjectRoleTransitionSimulator(
        project_id=project_id,
        user=user,
        roles=[lead],
        permission_map={"project_lead": ["project.release"]},
    )

    result = simulator.simulate(remove_role_assignment_ids=[lead.role_assignment_id])

    impact = result["permission_impacts"][0]
    assert impact["before"]["decision"] == "allow"
    assert impact["after"]["decision"] == "not_granted"
    assert impact["became_denied"] is True
    assert result["baseline_roles"]["active_roles"][0]["role_type"] == "project_lead"
    assert result["simulated_roles"]["active_roles"] == []


def test_role_change_cannot_override_explicit_deny():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User", weight=1000)
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
    )
    lead = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="project_lead")
    simulator = ProjectOSProjectRoleTransitionSimulator(
        project_id=project_id,
        user=user,
        base_assignments=[deny],
        permission_map={"project_lead": ["project.release"]},
    )

    result = simulator.simulate(add_roles=[lead], permissions=["project.release"])

    impact = result["permission_impacts"][0]
    assert impact["before"]["decision"] == "deny"
    assert impact["after"]["decision"] == "deny"
    assert impact["decision_changed"] is False
    assert impact["after"]["weight_used_for_decision"] is False


def test_replace_deputy_with_successor_changes_permission_set():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("User")
    deputy = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    successor = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="successor")
    simulator = ProjectOSProjectRoleTransitionSimulator(
        project_id=project_id,
        user=user,
        roles=[deputy],
        permission_map={
            "deputy": ["project.edit"],
            "successor": ["project.prepare_handover"],
        },
    )

    result = simulator.simulate(
        add_roles=[successor],
        remove_role_assignment_ids=[deputy.role_assignment_id],
    )

    impacts = {item["permission"]: item for item in result["permission_impacts"]}
    assert impacts["project.edit"]["before"]["decision"] == "allow"
    assert impacts["project.edit"]["after"]["decision"] == "not_granted"
    assert impacts["project.prepare_handover"]["before"]["decision"] == "not_granted"
    assert impacts["project.prepare_handover"]["after"]["decision"] == "allow"
    assert result["changed_permission_count"] == 2
