from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_change_trace import ProjectOSUserManagementChangeTraceEmitter
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext


def _service():
    manager = DinEditorProjectManager()
    correlation_id = str(uuid4())
    emitter = ProjectOSUserManagementChangeTraceEmitter(
        manager,
        correlation_id=correlation_id,
    )
    service = ProjectOSUserManagementChangeService(manager, on_change=emitter)
    return manager, emitter, service, correlation_id


def test_successful_changes_emit_correlated_bus_audit_and_command_history():
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
    assert len(emitter.command_history.all()) == 5
    assert {message.correlation_id for message in emitter.messages} == {correlation_id}
    assert len({trace.command_id for trace in emitter.traces}) == 5

    weight_trace = emitter.traces[2]
    assert weight_trace.operation == "user_weight_changed"
    assert weight_trace.reference == first.user_id
    assert weight_trace.actor_user_id == first.user_id
    assert weight_trace.message.payload["command_id"] == weight_trace.command_id
    assert weight_trace.message.payload["domain"]["weight"] == 350
    assert weight_trace.message.payload["actor_source"] == "domain"

    weight_record = emitter.command_history.all()[2]
    assert weight_record.command_id == weight_trace.command_id
    assert weight_record.reference == first.user_id
    assert weight_record.reversible is True
    assert dict(weight_record.before_values) == {"weight": 100}
    assert dict(weight_record.after_values) == {"weight": 350}
    assert weight_record.message_id == weight_trace.message.message_id

    role_trace = emitter.traces[3]
    assert role_trace.reference == role.role_assignment_id
    assert role_trace.actor_user_id == first.user_id
    assert emitter.command_history.all()[3].reversible is False

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


def test_explicit_command_context_overrides_actor_and_keeps_per_command_identity():
    manager, emitter, service, default_correlation_id = _service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer")
    correlation_id = str(uuid4())
    first_context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=correlation_id,
    )
    second_context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=correlation_id,
    )

    service.change_user_weight(target.user_id, 425, command_context=first_context)
    first_context_message = emitter.messages[-1]
    first_context_trace = emitter.traces[-1]

    assignment = service.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        source_reference="admin:test",
        command_context=second_context,
    )
    second_context_message = emitter.messages[-1]
    second_context_trace = emitter.traces[-1]

    assert default_correlation_id != correlation_id
    assert first_context.command_id != second_context.command_id
    assert first_context_trace.command_id == first_context.command_id
    assert first_context_trace.reference == target.user_id
    assert first_context_trace.actor_user_id == administrator.user_id
    assert first_context_message.correlation_id == correlation_id
    assert first_context_message.causation_id is None
    assert first_context_message.payload["actor_source"] == "command_context"
    assert first_context_trace.audit_entry["correlation_id"] == correlation_id
    assert first_context_trace.audit_entry["value"] == administrator.user_id

    assert second_context_trace.command_id == second_context.command_id
    assert second_context_trace.reference == assignment.assignment_id
    assert second_context_trace.actor_user_id == administrator.user_id
    assert second_context_message.correlation_id == correlation_id
    assert second_context_message.causation_id == first_context_message.message_id
    assert second_context_trace.audit_entry["correlation_id"] == correlation_id

    weight_record = emitter.command_history.get(first_context.command_id)
    permission_record = emitter.command_history.get(second_context.command_id)
    assert weight_record is not None
    assert weight_record.reversible is True
    assert dict(weight_record.before_values) == {"weight": 100}
    assert dict(weight_record.after_values) == {"weight": 425}
    assert permission_record is not None
    assert permission_record.reversible is False
    assert dict(permission_record.before_values) == {}
    assert dict(permission_record.after_values) == {}


def test_reusing_same_command_context_is_rejected_before_second_mutation():
    manager, emitter, service, _ = _service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer")
    context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=str(uuid4()),
    )

    service.change_user_weight(target.user_id, 300, command_context=context)
    before = manager.user_management.as_dict()
    trace_count = len(emitter.traces)
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())

    with pytest.raises(ValueError, match="command_id already used"):
        service.change_user_weight(target.user_id, 400, command_context=context)

    assert manager.user_management.as_dict() == before
    assert len(emitter.traces) == trace_count
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count


def test_explicit_command_context_can_set_initial_causation_id():
    manager, emitter, service, _ = _service()
    administrator = service.create_user("Administrator")
    target = service.create_user("Zielbenutzer")
    correlation_id = str(uuid4())
    causation_id = str(uuid4())
    context = ProjectOSUserManagementCommandContext(
        actor_user_id=administrator.user_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )

    service.change_user_weight(target.user_id, 510, command_context=context)

    trace = emitter.traces[-1]
    assert trace.command_id == context.command_id
    assert trace.message.correlation_id == correlation_id
    assert trace.message.causation_id == causation_id
    assert trace.audit_entry["causation_id"] == causation_id
    record = emitter.command_history.get(context.command_id)
    assert record is not None
    assert record.causation_id == causation_id


def test_command_context_rejects_invalid_identifiers_before_mutation():
    manager, emitter, service, _ = _service()
    user = service.create_user("Benutzer")
    before = manager.user_management.as_dict()
    trace_count = len(emitter.traces)

    with pytest.raises(ValueError, match="actor_user_id must be a UUID"):
        ProjectOSUserManagementCommandContext(
            actor_user_id="administrator",
            correlation_id=str(uuid4()),
        )

    with pytest.raises(ValueError, match="command_id must be a UUID"):
        ProjectOSUserManagementCommandContext(
            actor_user_id=user.user_id,
            correlation_id=str(uuid4()),
            command_id="not-a-command-id",
        )

    assert manager.user_management.as_dict() == before
    assert len(emitter.traces) == trace_count
    assert user.user_id == manager.user_management.users[0].user_id


def test_failed_command_emits_no_message_audit_or_command_history():
    manager, emitter, service, _ = _service()
    user = service.create_user("Benutzer")
    trace_count = len(emitter.traces)
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())

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
    assert len(emitter.command_history.all()) == history_count

    service.change_user_weight(user.user_id, 275)
    assert emitter.traces[-1].reference == user.user_id
    assert emitter.traces[-1].message.payload["domain"]["weight"] == 275


def test_approval_and_post_review_actor_are_taken_from_domain_objects_and_not_reversible():
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
    request_record, approval_record, review_record = emitter.command_history.all()[-3:]
    assert request_trace.reference == request.action_id
    assert request_trace.actor_user_id == requester.user_id
    assert approval_trace.reference == approval.approval_id
    assert approval_trace.actor_user_id == approver.user_id
    assert review_trace.reference == review.review_id
    assert review_trace.actor_user_id == reviewer.user_id
    assert request_record.reversible is False
    assert approval_record.reversible is False
    assert review_record.reversible is False
