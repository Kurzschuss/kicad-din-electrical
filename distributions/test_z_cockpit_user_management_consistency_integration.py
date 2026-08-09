from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_attention import ZCockpitAttentionView
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview


def _manager_with_mismatch() -> DinEditorProjectManager:
    manager = DinEditorProjectManager()
    owner = ProjectOSUserProfile(display_name="Projektleiter")
    other = ProjectOSUserProfile(display_name="Stellvertretung")
    role = ProjectOSUserProjectRole(
        project_id=manager.project_id,
        user_id=owner.user_id,
        role_type="deputy",
    )
    activation = ProjectOSProjectRoleActivation(
        project_id=manager.project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=other.user_id,
        reason="manual",
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(owner, other),
        project_roles=(role,),
        activations=(activation,),
    ))
    return manager


def test_project_lead_overview_turns_red_for_user_management_consistency_error():
    manager = _manager_with_mismatch()
    state = ZCockpitProjectLeadOverview(manager).state()
    assert state["traffic_light"] == "red"
    assert state["summary"]["user_management_consistency_red_count"] == 1
    assert state["user_management_consistency"]["issues"][0]["code"] == "UM_ACTIVATION_USER_MISMATCH"


def test_attention_exposes_consistency_error_with_direct_navigation():
    manager = _manager_with_mismatch()
    result = ZCockpitAttentionView(ZCockpitProjectLeadOverview(manager)).state()
    item = next(item for item in result["items"] if item["code"] == "UM_ACTIVATION_USER_MISMATCH")
    assert item["traffic_light"] == "red"
    assert item["priority"] == 30
    assert item["detail_target"]["view"] == "user_management_consistency"


def test_navigation_resolves_user_management_consistency_read_only():
    manager = _manager_with_mismatch()
    target = ZCockpitNavigationTarget(view="user_management_consistency", project_id=manager.project_id)
    result = ZCockpitNavigationResolver(manager).resolve(target)
    assert result["resolved_view"] == "user_management_consistency"
    assert result["payload"]["traffic_light"] == "red"
    assert result["payload"]["read_only"] is True
