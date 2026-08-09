from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_role_approval import ProjectOSRoleActionApprovalRequest
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .z_cockpit_navigation import ZCockpitNavigationTarget
from .z_cockpit_navigation_resolver import ZCockpitNavigationResolver


def test_approval_trace_navigation_requires_correlation_and_action_id():
    project_id = str(uuid4())
    with pytest.raises(ValueError, match="correlation_id"):
        ZCockpitNavigationTarget(
            view="approval_trace",
            project_id=project_id,
            metadata={"action_id": str(uuid4())},
        )
    with pytest.raises(ValueError, match="action_id"):
        ZCockpitNavigationTarget(
            view="approval_trace",
            project_id=project_id,
            correlation_id=str(uuid4()),
        )


def test_resolver_opens_exact_correlated_approval_trace():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    request = ProjectOSRoleActionApprovalRequest(
        project_id=manager.project_id,
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter(manager.sync_log).emit(
        request, correlation_id=correlation_id
    )
    target = ZCockpitNavigationTarget(
        view="approval_trace",
        project_id=manager.project_id,
        correlation_id=correlation_id,
        metadata={"action_id": request.action_id},
    )

    resolved = ZCockpitNavigationResolver(manager, messages=trace.messages).resolve(target)

    assert resolved["resolved_view"] == "approval_trace"
    assert resolved["payload"]["action_id"] == request.action_id
    assert resolved["payload"]["correlation_id"] == correlation_id
    assert resolved["payload"]["status"] == "pending_approval"
    assert resolved["payload"]["attention_required"] is True
    assert resolved["payload"]["audit_entry_count"] == 2
