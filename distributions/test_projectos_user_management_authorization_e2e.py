from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_policy import ProjectOSUserManagementCommandPolicy
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_user_management_command_diagnostics import (
    ZCockpitUserManagementCommandDiagnosticsView,
)

WEIGHT_CHANGE = "project.user_management.weight.change"
WEIGHT_UNDO = "project.user_management.weight.undo"
WEIGHT_REDO = "project.user_management.weight.redo"


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def _weight(manager: DinEditorProjectManager, user_id: str) -> int:
    return next(user.weight for user in manager.user_management.users if user.user_id == user_id)


def test_role_approval_command_undo_redo_audit_and_z_cockpit_end_to_end():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    principal = bootstrap.create_user("Projektleiter")
    deputy = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Vertrauensperson")
    target = bootstrap.create_user("Zielbenutzer", weight=100)

    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=principal.user_id,
        source_reference="e2e:deputy",
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="absence",
        triggered_by_user_id=principal.user_id,
        trigger_reference="e2e:activation",
    )
    request = bootstrap.command_request_approval(
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T10:00:00+00:00",
        reason="Stellvertretung freigeben",
    )
    bootstrap.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T10:01:00+00:00",
    )

    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_permission_map={"deputy": (WEIGHT_CHANGE, WEIGHT_UNDO, WEIGHT_REDO)},
        role_risk_class_map={"deputy": "high"},
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)

    runtime.changes.change_user_weight(
        target.user_id,
        500,
        command_context=_context(deputy.user_id),
    )
    assert _weight(manager, target.user_id) == 500
    assert runtime.changes.last_authorization["decision"] == "allow"
    assert runtime.changes.last_authorization["role_derived_assignment_count"] == 3
    assert runtime.changes.latest_authorization_evidence.effective_sources[0]["source_type"] == "role"

    undo = runtime.undo_redo.undo_latest(actor_user_id=deputy.user_id)
    assert _weight(manager, target.user_id) == 100
    assert runtime.emitter.command_history.get(undo.command_id).history_action == "undo"

    redo = runtime.undo_redo.redo_latest(actor_user_id=deputy.user_id)
    assert _weight(manager, target.user_id) == 500
    assert runtime.emitter.command_history.get(redo.command_id).history_action == "redo"

    assert len(runtime.emitter.traces) == 3
    assert len(runtime.emitter.messages) == 3
    assert len(manager.sync_log.entries) == 3
    assert len(runtime.changes.authorization_evidence) == 3
    assert {
        item.command_id for item in runtime.changes.authorization_evidence
    } == {
        item.command_id for item in runtime.emitter.traces
    }

    cockpit = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()
    assert cockpit["last_decision"] == "allow"
    assert cockpit["authorization_evidence_count"] == 3
    assert cockpit["can_undo"] is True
    assert cockpit["can_redo"] is False
    assert cockpit["trace_count"] == 3

    bootstrap.command_assign_permission(
        user_id=deputy.user_id,
        permission=WEIGHT_CHANGE,
        source_type="blacklist",
        effect="deny",
        risk_class="critical",
        source_reference="e2e:block",
    )
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    evidence_count = len(runtime.changes.authorization_evidence)

    with pytest.raises(PermissionError, match=r"\(deny\)"):
        runtime.changes.change_user_weight(
            target.user_id,
            650,
            command_context=_context(deputy.user_id),
        )

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(runtime.changes.authorization_evidence) == evidence_count
    denied = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()
    assert denied["last_decision"] == "deny"
    assert denied["deny_blocked"] is True
    assert denied["traffic_light"] == "yellow"
