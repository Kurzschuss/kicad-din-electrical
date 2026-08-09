from uuid import uuid4

import pytest

from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_user_management_persistence import (
    DERIVED_NOT_PERSISTED,
    ProjectOSUserManagementState,
    USER_MANAGEMENT_PERSISTENCE_VERSION,
)
from .projectos_user_project_roles import ProjectOSUserProjectRole


def _state():
    project_id = str(uuid4())
    lead = ProjectOSUserProfile("Leitung", weight=900)
    deputy = ProjectOSUserProfile("Vertretung", weight=700)
    reviewer = ProjectOSUserProfile("Prüfung", weight=500)
    role = ProjectOSUserProjectRole(
        project_id=project_id,
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=lead.user_id,
    )
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=deputy.user_id,
        reason="emergency",
        valid_from="2026-08-09T00:00:00+00:00",
        triggered_by_user_id=lead.user_id,
    )
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=deputy.user_id,
        reason="principal_returned",
        ended_at="2026-08-09T04:00:00+00:00",
        triggered_by_user_id=lead.user_id,
    )
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=f"activation:{activation.activation_id}",
        requested_by_user_id=lead.user_id,
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=reviewer.user_id,
        decision="approve",
        decided_at="2026-08-09T00:10:00+00:00",
    )
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=reviewer.user_id,
        result="confirmed",
        reviewed_at="2026-08-09T00:20:00+00:00",
    )
    permission = ProjectOSPermissionAssignment(
        user_id=deputy.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    return ProjectOSUserManagementState(
        project_id=project_id,
        users=(lead, deputy, reviewer),
        permission_assignments=(permission,),
        project_roles=(role,),
        activations=(activation,),
        deactivations=(deactivation,),
        approval_requests=(request,),
        approvals=(approval,),
        post_reviews=(review,),
    )


def test_user_management_state_roundtrip_preserves_ids_and_weight():
    state = _state()
    payload = state.as_dict()
    restored = ProjectOSUserManagementState.from_dict(payload)

    assert payload["version"] == USER_MANAGEMENT_PERSISTENCE_VERSION
    assert restored.as_dict() == payload
    assert restored.users[0].weight == 900
    assert restored.activations[0].role_assignment_id == restored.project_roles[0].role_assignment_id
    assert restored.approvals[0].action_id == restored.approval_requests[0].action_id
    assert restored.post_reviews[0].action_id == restored.approval_requests[0].action_id


def test_derived_views_are_explicitly_excluded_from_persistence():
    payload = _state().as_dict()
    assert set(payload["derived_not_persisted"]) == set(DERIVED_NOT_PERSISTED)
    assert "simulations" in DERIVED_NOT_PERSISTED
    assert "z_cockpit_views" in DERIVED_NOT_PERSISTED
    assert "materialized_role_knowledge" in DERIVED_NOT_PERSISTED
    assert "approval_traces" in DERIVED_NOT_PERSISTED


def test_persistence_rejects_activation_with_unknown_role():
    state = _state()
    activation = ProjectOSProjectRoleActivation(
        project_id=state.project_id,
        role_assignment_id=str(uuid4()),
        user_id=state.users[1].user_id,
        reason="manual",
    )
    with pytest.raises(ValueError, match="unknown role_assignment_id"):
        ProjectOSUserManagementState(
            project_id=state.project_id,
            users=state.users,
            project_roles=state.project_roles,
            activations=(activation,),
        )


def test_persistence_rejects_approval_without_request():
    state = _state()
    approval = ProjectOSRoleActionApproval(
        action_id=str(uuid4()),
        approver_user_id=state.users[2].user_id,
        decision="approve",
        decided_at="2026-08-09T00:10:00+00:00",
    )
    with pytest.raises(ValueError, match="unknown action_id"):
        ProjectOSUserManagementState(
            project_id=state.project_id,
            users=state.users,
            approvals=(approval,),
        )


def test_persistence_rejects_foreign_project_role():
    state = _state()
    foreign = ProjectOSUserProjectRole(
        project_id=str(uuid4()),
        user_id=state.users[1].user_id,
        role_type="deputy",
    )
    with pytest.raises(ValueError, match="another project"):
        ProjectOSUserManagementState(
            project_id=state.project_id,
            users=state.users,
            project_roles=(foreign,),
        )


def test_unknown_persistence_version_is_rejected():
    payload = _state().as_dict()
    payload["version"] = 99
    with pytest.raises(ValueError, match="unsupported user management persistence version"):
        ProjectOSUserManagementState.from_dict(payload)
