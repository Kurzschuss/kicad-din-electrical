from uuid import uuid4

from .din_editor_sync_log import DinSyncLog
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_role_approval_trace import ProjectOSRoleApprovalTraceEmitter
from .z_cockpit_role_approval_trace import ZCockpitRoleApprovalTraceView


def test_freigabevorgang_zeigt_anforderung_entscheidung_und_wirksamkeit():
    project_id = str(uuid4())
    correlation_id = str(uuid4())
    requester = str(uuid4())
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=requester,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=str(uuid4()),
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter(DinSyncLog()).emit(
        request, [approval], correlation_id=correlation_id
    )

    state = ZCockpitRoleApprovalTraceView(
        messages=trace.messages,
        audit_entries=trace.audit_entries,
    ).state(project_id=project_id, correlation_id=correlation_id, action_id=request.action_id)

    assert state["found"] is True
    assert state["status"] == "approved"
    assert state["attention_required"] is False
    assert [item["label"] for item in state["timeline"]] == [
        "Freigabe angefordert",
        "Freigabe entschieden",
        "Wirksamkeit bewertet",
    ]
    assert state["timeline"][1]["causation_id"] == state["timeline"][0]["message_id"]
    assert state["timeline"][2]["causation_id"] == state["timeline"][1]["message_id"]
    assert state["audit_entry_count"] == 3


def test_notfallnachpruefung_bleibt_als_aufmerksamkeit_sichtbar():
    project_id = str(uuid4())
    correlation_id = str(uuid4())
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="deactivation",
        target_reference=f"deactivation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="critical",
        requested_at="2026-08-09T00:00:00+00:00",
        emergency=True,
    )
    trace = ProjectOSRoleApprovalTraceEmitter(DinSyncLog()).emit(
        request, correlation_id=correlation_id
    )
    state = ZCockpitRoleApprovalTraceView(
        messages=trace.messages,
        audit_entries=trace.audit_entries,
    ).state(project_id=project_id, correlation_id=correlation_id, action_id=request.action_id)

    assert state["status"] == "emergency_pending_review"
    assert state["post_review_required"] is True
    assert state["attention_required"] is True
    assert state["decisions"] == []


def test_andere_projekte_und_vorgaenge_werden_nicht_eingemischt():
    project_id = str(uuid4())
    correlation_id = str(uuid4())
    request = ProjectOSRoleActionApprovalRequest(
        project_id=project_id,
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=str(uuid4()),
        risk_class="low",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    trace = ProjectOSRoleApprovalTraceEmitter(DinSyncLog()).emit(request, correlation_id=correlation_id)
    view = ZCockpitRoleApprovalTraceView(messages=trace.messages, audit_entries=trace.audit_entries)

    state = view.state(
        project_id=project_id,
        correlation_id=str(uuid4()),
        action_id=request.action_id,
    )
    assert state["found"] is False
    assert state["message_count"] == 0
    assert state["audit_entry_count"] == 0
