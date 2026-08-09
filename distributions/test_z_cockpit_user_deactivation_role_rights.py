from datetime import datetime, timezone
from uuid import uuid4

from .projectos_authorization import ProjectOSUserProfile
from .projectos_role_activation import ProjectOSProjectRoleActivation
from .projectos_user_deactivation import ProjectOSUserDeactivation
from .projectos_user_project_roles import ProjectOSUserProjectRole
from .z_cockpit_approved_role_activation import ZCockpitApprovedRoleActivationView


def test_deactivated_user_keeps_active_role_history_but_exposes_no_role_right():
    project_id = str(uuid4())
    actor = ProjectOSUserProfile("Projektleitung")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
        triggered_by_user_id=actor.user_id,
    )
    deactivation = ProjectOSUserDeactivation(
        project_id=project_id,
        user_id=user.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=actor.user_id,
        reason="Offboarding",
    )
    view = ZCockpitApprovedRoleActivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        permission_map={"deputy": ["project.release"]},
        risk_class_map={"deputy": "low"},
        user_deactivations=[deactivation],
    )
    state = view.state(at=datetime(2026, 8, 9, 12, 1, tzinfo=timezone.utc))

    assert len(state["effective_activations"]) == 1
    assert state["user_deactivated"] is True
    assert state["rights"] == []
    assert state["user_deactivation"]["deactivation_id"] == deactivation.deactivation_id
