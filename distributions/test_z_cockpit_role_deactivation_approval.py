from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_approval import ProjectOSRoleActionApprovalRequest
from distributions.projectos_role_deactivation import ProjectOSProjectRoleDeactivation
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_role_deactivation_approval import ZCockpitRoleDeactivationApprovalView


def test_z_cockpit_shows_blocked_critical_deactivation_and_emergency_review():
    project_id = str(uuid4())
    principal = ProjectOSUserProfile("Projektleiter")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
    )
    deactivation = ProjectOSProjectRoleDeactivation(
        activation_id=activation.activation_id,
        project_id=project_id,
        user_id=user.user_id,
        reason="principal_returned",
        ended_at="2026-08-09T00:00:00+00:00",
        triggered_by_user_id=principal.user_id,
    )
    now = datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)

    blocked = ZCockpitRoleDeactivationApprovalView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        deactivations=[deactivation],
    ).state(at=now, risk_class="critical")
    assert blocked["deactivation_approvals"][0]["approval_status"] == "approval_missing"
    assert blocked["deactivation_approvals"][0]["effective"] is False
    assert blocked["attention_required"] is True
    assert len(blocked["effective_roles"]) == 1

    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{deactivation.deactivation_id}",
        requested_by_user_id=principal.user_id,
        risk_class="critical",
        requested_at="2026-08-08T23:58:00+00:00",
        emergency=True,
    )
    emergency = ZCockpitRoleDeactivationApprovalView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        deactivations=[deactivation],
        approval_requests=[request],
    ).state(at=now, risk_class="critical")
    item = emergency["deactivation_approvals"][0]
    assert item["approval_status"] == "emergency_pending_review"
    assert item["effective"] is True
    assert item["post_review_required"] is True
    assert emergency["pending_post_reviews"] == [deactivation.deactivation_id]
    assert emergency["effective_roles"] == []
