from datetime import datetime, timezone
from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from .projectos_role_post_review import ProjectOSRoleEmergencyPostReview
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_user_management_consistency import ZCockpitUserManagementConsistencyView


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_consistency_view_is_green_for_empty_valid_state():
    manager = DinEditorProjectManager()
    result = ZCockpitUserManagementConsistencyView(manager).state()
    assert result["traffic_light"] == "green"
    assert result["consistent"] is True
    assert result["issue_count"] == 0


def test_consistency_view_detects_activation_and_deactivation_user_scope_mismatches():
    manager = DinEditorProjectManager()
    user_a = ProjectOSUserProfile(display_name="Projektleiter")
    user_b = ProjectOSUserProfile(display_name="Stellvertretung")
    role = ProjectOSUserProjectRole(
        project_id=manager.project_id,
        user_id=user_a.user_id,
        role_type="deputy",
        scope="project",
    )
    activation = ProjectOSProjectRoleActivation(
        project_id=manager.project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user_b.user_id,
        reason="manual",
        scope="section:A",
    )
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=manager.project_id,
        user_id=user_a.user_id,
        reason="manual_return",
        ended_at=_now(),
        scope="project",
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(user_a, user_b),
        project_roles=(role,),
        activations=(activation,),
        deactivations=(deactivation,),
    ))

    result = ZCockpitUserManagementConsistencyView(manager).state()
    codes = {item["code"] for item in result["issues"]}
    assert result["traffic_light"] == "red"
    assert "UM_ACTIVATION_USER_MISMATCH" in codes
    assert "UM_ACTIVATION_SCOPE_MISMATCH" in codes
    assert "UM_DEACTIVATION_USER_MISMATCH" in codes
    assert "UM_DEACTIVATION_SCOPE_MISMATCH" in codes


def test_consistency_view_detects_invalid_post_review_semantics():
    manager = DinEditorProjectManager()
    requester = ProjectOSUserProfile(display_name="Anforderer")
    request = ProjectOSRoleActionApprovalRequest(
        project_id=manager.project_id,
        action_type="activation",
        target_reference=str(uuid4()),
        requested_by_user_id=requester.user_id,
        risk_class="high",
        requested_at=_now(),
        emergency=False,
    )
    review = ProjectOSRoleEmergencyPostReview(
        action_id=request.action_id,
        reviewer_user_id=requester.user_id,
        result="confirmed",
        reviewed_at=_now(),
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(requester,),
        approval_requests=(request,),
        post_reviews=(review,),
    ))

    result = ZCockpitUserManagementConsistencyView(manager).state()
    codes = {item["code"] for item in result["issues"]}
    assert "UM_POST_REVIEW_NON_EMERGENCY" in codes
    assert "UM_POST_REVIEW_SELF_REVIEW" in codes
    assert result["red_count"] == 2
