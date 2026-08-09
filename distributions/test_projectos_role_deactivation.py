from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator, ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_deactivation import ProjectOSProjectRoleDeactivation, ProjectOSProjectRoleLifecycleEvaluator
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole


def _dt(hour: int) -> datetime:
    return datetime(2026, 8, 9, hour, 0, tzinfo=timezone.utc)


def test_deactivation_removes_role_right_only_from_ended_at() -> None:
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
    lifecycle = ProjectOSProjectRoleLifecycleEvaluator(roles=[role], activations=[activation], deactivations=[deactivation])

    before = lifecycle.permission_assignments(project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_dt(5))
    after = lifecycle.permission_assignments(project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_dt(7))

    assert [item.permission for item in before] == ["project.release"]
    assert after == ()
    state = lifecycle.state(project_id=project_id, user=user, at=_dt(7))
    assert state["ended_activations"][0]["deactivation"]["reason"] == "principal_returned"


def test_deactivation_does_not_remove_direct_or_deny_assignments() -> None:
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(project_id=project_id, role_assignment_id=role.role_assignment_id, user_id=user.user_id, reason="manual")
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=user.user_id,
        reason="manual_return",
        ended_at=_dt(1).isoformat(),
    )
    lifecycle = ProjectOSProjectRoleLifecycleEvaluator(roles=[role], activations=[activation], deactivations=[deactivation])
    derived = lifecycle.permission_assignments(project_id=project_id, user=user, permission_map={"deputy": ["project.release"]}, at=_dt(2))
    direct = ProjectOSPermissionAssignment(user_id=user.user_id, permission="project.read", source_type="direct", effect="allow")
    deny = ProjectOSPermissionAssignment(user_id=user.user_id, permission="project.release", source_type="deny", effect="deny")
    evaluator = ProjectOSAuthorizationEvaluator((direct, deny) + derived)

    assert evaluator.evaluate(user, "project.read", at=_dt(2))["decision"] == "allow"
    assert evaluator.evaluate(user, "project.release", at=_dt(2))["decision"] == "deny"


def test_deactivation_requires_known_activation() -> None:
    user = ProjectOSUserProfile("Uwe")
    project_id = str(uuid4())
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=str(uuid4()),
        project_id=project_id,
        user_id=user.user_id,
        reason="revoked",
        ended_at=_dt(1).isoformat(),
    )
    try:
        ProjectOSProjectRoleLifecycleEvaluator(deactivations=[deactivation])
    except ValueError as exc:
        assert "unknown activation_id" in str(exc)
    else:
        raise AssertionError("unknown activation reference must fail")
