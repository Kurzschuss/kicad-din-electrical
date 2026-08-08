from uuid import uuid4

from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalRequest,
)
from .z_cockpit_role_approval import ZCockpitRoleActionApprovalView


def _request(*, emergency=False):
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference="activation:test",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=emergency,
    )


def test_pending_approval_is_attention_item():
    request = _request()
    result = ZCockpitRoleActionApprovalView().state(request)
    assert result["status_label"] == "Freigabe ausstehend"
    assert result["attention_required"] is True
    assert result["effective"] is False


def test_approved_state_is_explained():
    request = _request()
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    result = ZCockpitRoleActionApprovalView([approval]).state(request)
    assert result["status_label"] == "Freigegeben"
    assert result["attention_required"] is False
    assert result["effective"] is True


def test_emergency_state_requires_visible_post_review():
    request = _request(emergency=True)
    result = ZCockpitRoleActionApprovalView().state(request)
    assert result["post_review_required"] is True
    assert result["attention_required"] is True
    assert "Nachprüfung" in result["status_label"]
