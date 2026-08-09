from uuid import uuid4

from .din_editor_sync_log import DinSyncLog
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter


def _request(*, emergency=False):
    return ProjectOSRoleActionApprovalRequest(
        project_id=str(uuid4()),
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=emergency,
    )


def test_trace_keeps_one_project_and_correlation_across_bus_and_audit():
    request = _request()
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    audit = DinSyncLog()
    trace = ProjectOSRoleApprovalTraceEmitter(audit).emit(request, [approval])

    assert trace.approval_state["status"] == "approved"
    assert len(trace.messages) == 3
    assert len(trace.audit_entries) == 3
    assert all(item.project_id == request.project_id for item in trace.messages)
    assert all(item.correlation_id == trace.correlation_id for item in trace.messages)
    assert all(item["project_id"] == request.project_id for item in trace.audit_entries)
    assert all(item["correlation_id"] == trace.correlation_id for item in trace.audit_entries)
    assert audit.export() == list(trace.audit_entries)


def test_trace_forms_explicit_causation_chain():
    request = _request()
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="reject",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request, [approval])
    requested, decided, evaluated = trace.messages

    assert requested.causation_id is None
    assert decided.causation_id == requested.message_id
    assert evaluated.causation_id == decided.message_id
    assert trace.audit_entries[0]["causation_id"] == requested.message_id
    assert trace.audit_entries[1]["causation_id"] == requested.message_id
    assert trace.audit_entries[2]["causation_id"] == decided.message_id


def test_pending_approval_is_audited_without_inventing_decision_event():
    request = _request()
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request)

    assert [item.name for item in trace.messages] == [
        "projectos.role_action.approval_requested",
        "projectos.role_action.approval_effectiveness_evaluated",
    ]
    assert trace.approval_state["status"] == "pending_approval"
    assert trace.approval_state["effective"] is False
    assert [item["action"] for item in trace.audit_entries] == [
        "approval_requested",
        "approval_effectiveness_evaluated",
    ]


def test_emergency_pending_review_is_preserved_in_trace():
    request = _request(emergency=True)
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request)

    assert trace.approval_state["status"] == "emergency_pending_review"
    assert trace.approval_state["post_review_required"] is True
    assert trace.messages[-1].payload["post_review_required"] is True
    assert trace.audit_entries[-1]["value"] == "emergency_pending_review"


def test_foreign_approval_is_not_emitted_for_request():
    request = _request()
    foreign = ProjectOSRoleActionApproval(
        action_id=str(uuid4()),
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter().emit(request, [foreign])

    assert len(trace.messages) == 2
    assert trace.approval_state["external_approval_count"] == 0
