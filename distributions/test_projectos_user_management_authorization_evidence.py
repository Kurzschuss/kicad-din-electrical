from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_runtime import build_projectos_user_management_runtime


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def test_successful_authorization_evidence_links_command_message_and_audit_trace():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission="project.user_management.weight.change",
        source_type="direct",
        effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(administrator.user_id)

    runtime.changes.change_user_weight(target.user_id, 450, command_context=context)

    evidence = runtime.changes.latest_authorization_evidence
    trace = runtime.emitter.traces[-1]
    assert evidence is not None
    assert evidence.command_id == context.command_id == trace.command_id
    assert evidence.correlation_id == context.correlation_id == trace.message.correlation_id
    assert evidence.message_id == trace.message.message_id
    assert evidence.audit_reference == trace.audit_entry["reference"]
    assert evidence.required_permission == "project.user_management.weight.change"
    assert evidence.decision == "allow"
    assert evidence.as_dict()["persisted"] is False
    assert runtime.state()["authorization_evidence_count"] == 1


def test_denied_authorization_has_diagnostic_decision_but_no_success_evidence_or_trace():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(administrator.user_id)

    with pytest.raises(PermissionError, match="not_granted"):
        runtime.changes.change_user_weight(target.user_id, 450, command_context=context)

    assert runtime.changes.last_authorization["decision"] == "not_granted"
    assert runtime.changes.authorization_evidence == ()
    assert runtime.emitter.traces == []
    assert runtime.emitter.messages == []
    assert manager.sync_log.entries == []


def test_authorization_evidence_resets_with_user_management_runtime_generation(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission="project.user_management.weight.change",
        source_type="direct",
        effect="allow",
    )
    path = manager.save(tmp_path / "project.json")
    runtime = build_projectos_user_management_runtime(manager)
    runtime.changes.change_user_weight(target.user_id, 300, command_context=_context(administrator.user_id))
    assert len(runtime.changes.authorization_evidence) == 1

    manager.load(path, discard_changes=True)

    assert runtime.changes.authorization_evidence == ()
    assert runtime.changes.last_authorization is None
