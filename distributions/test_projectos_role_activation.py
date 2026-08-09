from datetime import datetime, timezone
from uuid import uuid4

import pytest

from distributions.projectos_authorization import ProjectOSAuthorizationEvaluator, ProjectOSPermissionAssignment, ProjectOSUserProfile
from distributions.projectos_role_activation import (
    ProjectOSProjectRoleActivation,
    ProjectOSProjectRoleActivationRegistry,
)
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole


def _now():
    return datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)


def test_assigned_role_without_activation_has_no_permission_effect():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    registry = ProjectOSProjectRoleActivationRegistry([role], [])

    state = registry.state(project_id=project_id, user=user, at=_now())
    assignments = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
    )

    assert state["activated_roles"] == []
    assert len(state["assigned_not_activated_roles"]) == 1
    assert assignments == ()


def test_matching_activation_enables_role_permissions_with_activation_origin():
    project_id = str(uuid4())
    trigger_user = ProjectOSUserProfile("Projektleiter")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
        triggered_by_user_id=trigger_user.user_id,
        trigger_reference="absence-case-17",
    )
    registry = ProjectOSProjectRoleActivationRegistry([role], [activation])

    assignments = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
        risk_class="high",
    )

    assert len(assignments) == 1
    item = assignments[0]
    assert item.permission == "project.release"
    assert item.metadata["activation_id"] == activation.activation_id
    assert item.metadata["activation_reason"] == "absence"
    assert item.metadata["triggered_by_user_id"] == trigger_user.user_id
    assert item.metadata["trigger_reference"] == "absence-case-17"


def test_expired_activation_does_not_enable_permission():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Nachfolger")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="successor")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="succession",
        valid_until="2026-08-08T23:00:00+00:00",
    )
    registry = ProjectOSProjectRoleActivationRegistry([role], [activation])

    state = registry.state(project_id=project_id, user=user, at=_now())
    assignments = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"successor": ["project.release"]},
        at=_now(),
    )

    assert state["activated_roles"] == []
    assert len(state["inactive_activations"]) == 1
    assert assignments == ()


def test_activation_must_reference_existing_role():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Stellvertretung")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=str(uuid4()),
        user_id=user.user_id,
        reason="manual",
    )

    with pytest.raises(ValueError, match="unknown role_assignment_id"):
        ProjectOSProjectRoleActivationRegistry([], [activation])


def test_activated_allow_still_cannot_override_explicit_deny():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Stellvertretung", weight=950)
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="emergency",
    )
    registry = ProjectOSProjectRoleActivationRegistry([role], [activation])
    derived = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"deputy": ["project.release"]},
        at=_now(),
    )
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
    )

    result = ProjectOSAuthorizationEvaluator(derived + (deny,)).evaluate(
        user, "project.release", at=_now()
    )

    assert result["decision"] == "deny"
    assert result["allowed"] is False
    assert result["weight_used_for_decision"] is False
