from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_change_trace import ProjectOSUserManagementChangeTraceEmitter


def _service():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    emitter = ProjectOSUserManagementChangeTraceEmitter(
        manager,
        correlation_id=correlation_id,
    )
    service = ProjectOSUserManagementChangeService(manager, on_change=emitter)
    return manager, emitter, service, correlation_id


def test_successful_changes_emit_correlated_bus_and_audit_chain():
    manager, emitter, service, correlation_id = _service()

    first = service.create_user("Erster Benutzer", weight=100)
    second = service.create_user("Zweiter Benutzer", weight=200)
    service.change_user_weight(first.user_id, 350)
    role = service.command_assign_project_role(
        user_id=second.user_id,
        role_type="deputy",
        assigned_by_user_id=first.user_id,
        source_reference="test:assignment",
    )
    activation = service.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="vacation",
        triggered_by_user_id=first.user_id,
        trigger_reference="test:activation",
    )

    assert len(emitter.traces) == 5
    assert len(emitter.messages) == 5
    assert len(manager.sync_log.entries) == 5
    assert {message.correlation_id for message in emitter.messages} == {correlation_id}

    weight_trace = emitter.traces[2]
    assert weight_trace.operation == "user_weight_changed"
    assert weight_trace.reference == first.user_id
    assert weight_trace.actor_user_id == first.user_id
    assert weight_trace.message.payload["domain"]["weight"] == 350

    role_trace = emitter.traces[3]
    assert role_trace.reference == role.role_assignment_id
    assert role_trace.actor_user_id == first.user_id

    activation_trace = emitter.traces[4]
    assert activation_trace.reference == activation.activation_id
    assert activation_trace.actor_user_id == first.user_id

    for index in range(1, len(emitter.messages)):
        assert emitter.messages[index].causation_id == emitter.messages[index - 1].message_id

    for trace in emitter.traces:
        assert trace.audit_entry["project_id"] == manager.project_id
        assert trace.audit_entry["correlation_id"] == correlation_id
        assert trace.audit_entry["reference"] == trace.reference
        assert trace.audit_entry["action"] == trace.operation


def test_failed_command_emits_no_message_or_audit_and_keeps_trace_snapshot_clean():
    manager, emitter, service, _ = _service()
    user = service.create_user("Benutzer")
    trace_count = len(emitter.traces)
    audit_count = len(manager.sync_log.entries)

    with pytest.raises(ValueError, match="unknown user_id"):
        service.command_assign_permission(
            user_id=str(uuid4()),
            permission="project.release",
            source_type="direct",
            effect="allow",
        )

    assert len(emitter.traces) == trace_count
    assert len(emitter.messages) == trace_count
    assert len(manager.sync_log.entries) == audit_count

    service.change_user_weight(user.user_id, 275)
    assert emitter.traces[-1].reference == user.user_id
    assert emitter.traces[-1].message.payload["domain"]["weight"] == 275


def test_approval_and_post_review_actor_are_taken_from_domain_objects():
    manager, emitter, service, _ = _service()
    requester = service.create_user("Anforderer")
    approver = service.create_user("Freigeber")
    reviewer = service.create_user("Pruefer")

    request = service.command_request_approval(
        action_type="activation",
        target_reference=str(uuid4()),
        requested_by_user_id=requester.user_id,
        risk_class="critical",
        requested_at="2026-08-09T01:00:00+00:00",
        emergency=True,
        reason="Notfall",
    )
    approval = service.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T01:05:00+00:00",
    )
    review = service.command_complete_post_review(
        action_id=request.action_id,
        reviewer_user_id=reviewer.user_id,
        result="confirmed",
        reviewed_at="2026-08-09T01:10:00+00:00",
    )

    request_trace, approval_trace, review_trace = emitter.traces[-3:]
    assert request_trace.reference == request.action_id
    assert request_trace.actor_user_id == requester.user_id
    assert approval_trace.reference == approval.approval_id
    assert approval_trace.actor_user_id == approver.user_id
    assert review_trace.reference == review.review_id
    assert review_trace.actor_user_id == reviewer.user_id
