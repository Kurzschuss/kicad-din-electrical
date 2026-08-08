from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_role_deactivation import ZCockpitProjectRoleDeactivationView


def _dt(hour: int) -> datetime:
    return datetime(2026, 8, 9, hour, 0, tzinfo=timezone.utc)


def test_z_cockpit_simulates_return_and_permission_loss() -> None:
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="vacation",
        valid_from=_dt(0).isoformat(),
        valid_until=_dt(12).isoformat(),
    )
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=user.user_id,
        reason="principal_returned",
        ended_at=_dt(6).isoformat(),
    )
    view = ZCockpitProjectRoleDeactivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        permission_map={"deputy": ["project.release"]},
    )

    result = view.simulate_deactivation(deactivation, before_at=_dt(5), after_at=_dt(7))

    assert result["deactivation"]["reason_label"] == "Projektleiter zurückgekehrt"
    assert result["lost_permission_count"] == 1
    impact = result["permission_impacts"][0]
    assert impact["permission"] == "project.release"
    assert impact["before"]["allowed"] is True
    assert impact["after"] is None
    assert impact["lost_permission"] is True
    assert result["read_only"] is True


def test_z_cockpit_return_keeps_direct_permission_and_deny() -> None:
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(project_id=project_id, role_assignment_id=role.role_assignment_id, user_id=user.user_id, reason="manual")
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=user.user_id,
        reason="manual_return",
        ended_at=_dt(6).isoformat(),
    )
    direct = ProjectOSPermissionAssignment(user_id=user.user_id, permission="project.read", source_type="direct", effect="allow")
    deny = ProjectOSPermissionAssignment(user_id=user.user_id, permission="project.delete", source_type="deny", effect="deny")
    view = ZCockpitProjectRoleDeactivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        base_assignments=[direct, deny],
        permission_map={"deputy": ["project.release"]},
    )

    result = view.simulate_deactivation(deactivation, before_at=_dt(5), after_at=_dt(7))
    impacts = {item["permission"]: item for item in result["permission_impacts"]}

    assert impacts["project.read"]["remained_allowed"] is True
    assert impacts["project.delete"]["remained_denied"] is True
    assert impacts["project.release"]["lost_permission"] is True
