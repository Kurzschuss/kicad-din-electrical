from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import (
    ProjectOSAuthorizationEvaluator,
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)
from distributions.projectos_user_project_roles import (
    ProjectOSUserProjectRole,
    ProjectOSUserProjectRoleRegistry,
)


def test_project_role_state_respects_project_scope_and_validity():
    project_id = str(uuid4())
    other_project = str(uuid4())
    user = ProjectOSUserProfile("Projektleiter")
    registry = ProjectOSUserProjectRoleRegistry([
        ProjectOSUserProjectRole(project_id, user.user_id, "project_lead", scope="project"),
        ProjectOSUserProjectRole(project_id, user.user_id, "deputy", scope="subsystem"),
        ProjectOSUserProjectRole(other_project, user.user_id, "trusted_person", scope="project"),
        ProjectOSUserProjectRole(
            project_id,
            user.user_id,
            "successor",
            valid_until="2026-01-01T00:00:00+00:00",
        ),
    ])

    state = registry.state(
        project_id=project_id,
        user=user,
        scope="project",
        at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )

    assert [item["role_type"] for item in state["active_roles"]] == ["project_lead"]
    assert [item["role_type"] for item in state["inactive_roles"]] == ["successor"]


def test_project_role_preserves_assignment_origin():
    project_id = str(uuid4())
    assigner = ProjectOSUserProfile("Owner")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(
        project_id,
        user.user_id,
        "deputy",
        assigned_by_user_id=assigner.user_id,
        source_reference="governance:decision-42",
    )

    state = ProjectOSUserProjectRoleRegistry([role]).state(project_id=project_id, user=user)
    current = state["active_roles"][0]
    assert current["assigned_by_user_id"] == assigner.user_id
    assert current["source_reference"] == "governance:decision-42"


def test_project_roles_translate_to_normal_permission_assignments():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Vertrauensperson")
    registry = ProjectOSUserProjectRoleRegistry([
        ProjectOSUserProjectRole(project_id, user.user_id, "trusted_person")
    ])

    assignments = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"trusted_person": ("project.review_sensitive", "project.view_audit")},
    )

    assert {item.permission for item in assignments} == {"project.review_sensitive", "project.view_audit"}
    assert all(item.source_type == "role" for item in assignments)
    assert all(item.metadata["project_role"] == "trusted_person" for item in assignments)


def test_explicit_deny_still_overrides_project_role_allow():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Projektleiter", weight=900)
    registry = ProjectOSUserProjectRoleRegistry([
        ProjectOSUserProjectRole(project_id, user.user_id, "project_lead")
    ])
    role_assignments = registry.permission_assignments(
        project_id=project_id,
        user=user,
        permission_map={"project_lead": ("project.release",)},
        risk_class="critical",
    )
    deny = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.release",
        source_type="deny",
        effect="deny",
        scope="project",
        risk_class="critical",
        source_reference="four-eyes-lock",
    )

    result = ProjectOSAuthorizationEvaluator(role_assignments + (deny,)).evaluate(
        user,
        "project.release",
        scope="project",
    )

    assert result["decision"] == "deny"
    assert result["allowed"] is False
    assert result["weight_used_for_decision"] is False
