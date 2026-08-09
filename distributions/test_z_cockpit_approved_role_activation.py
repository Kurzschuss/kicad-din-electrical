from datetime import datetime, timezone
from uuid import uuid4

from distributions.projectos_authorization import ProjectOSUserProfile
from distributions.projectos_role_activation import ProjectOSProjectRoleActivation
from distributions.projectos_role_approval import ProjectOSRoleActionApproval, ProjectOSRoleActionApprovalRequest
from distributions.projectos_user_project_roles import ProjectOSUserProjectRole
from distributions.z_cockpit_approved_role_activation import ZCockpitApprovedRoleActivationView


def _now():
    return datetime(2026, 8, 9, 0, 0, tzinfo=timezone.utc)


def _setup():
    project_id = str(uuid4())
    trigger = ProjectOSUserProfile("Projektleiter")
    user = ProjectOSUserProfile("Stellvertretung")
    role = ProjectOSUserProjectRole(project_id=project_id, user_id=user.user_id, role_type="deputy")
    activation = ProjectOSProjectRoleActivation(
        project_id=project_id,
        role_assignment_id=role.role_assignment_id,
        user_id=user.user_id,
        reason="absence",
        triggered_by_user_id=trigger.user_id,
    )
    return project_id, trigger, user, role, activation


def test_blocked_high_risk_activation_is_visible_without_rights():
    project_id, _, user, role, activation = _setup()
    view = ZCockpitApprovedRoleActivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        permission_map={"deputy": ["project.release"]},
        risk_class_map={"deputy": "high"},
    )
    state = view.state(at=_now())
    assert state["rights"] == []
    assert state["blocked_activations"][0]["approval"]["status_label"] == "Freigabeauftrag fehlt"


def test_approved_high_risk_activation_exposes_effective_right():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    view = ZCockpitApprovedRoleActivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        approval_requests=[request],
        approvals=[approval],
        permission_map={"deputy": ["project.release"]},
        risk_class_map={"deputy": "high"},
    )
    state = view.state(at=_now())
    assert state["effective_activations"][0]["approval"]["status_label"] == "Freigegeben"
    assert state["rights"][0]["permission"] == "project.release"
    assert state["rights"][0]["allowed"] is True


def test_emergency_activation_stays_visible_as_open_post_review():
    project_id, trigger, user, role, activation = _setup()
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=trigger.user_id,
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )
    view = ZCockpitApprovedRoleActivationView(
        project_id=project_id,
        user=user,
        roles=[role],
        activations=[activation],
        approval_requests=[request],
        permission_map={"deputy": ["project.release"]},
        risk_class_map={"deputy": "critical"},
    )
    state = view.state(at=_now())
    assert state["post_review_required"] is True
    assert len(state["pending_post_reviews"]) == 1
    assert state["pending_post_reviews"][0]["approval"]["status_label"] == "Notfall vorläufig wirksam – Nachprüfung erforderlich"
    assert state["rights"][0]["allowed"] is True
