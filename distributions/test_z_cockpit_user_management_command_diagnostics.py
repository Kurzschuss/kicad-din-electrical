from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_project_lead_overview import ZCockpitProjectLeadOverview
from .z_cockpit_user_management_command_diagnostics import (
    ZCockpitUserManagementCommandDiagnosticsView,
)


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def _runtime(*, allow: bool):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Ziel", weight=100)
    if allow:
        bootstrap.command_assign_permission(
            user_id=administrator.user_id,
            permission="project.user_management.weight.change",
            source_type="direct",
            effect="allow",
        )
    runtime = build_projectos_user_management_runtime(manager)
    return manager, administrator, target, runtime


def test_z_cockpit_command_diagnostics_show_authorization_evidence_and_undo_availability():
    manager, administrator, target, runtime = _runtime(allow=True)
    runtime.changes.change_user_weight(
        target.user_id,
        400,
        command_context=_context(administrator.user_id),
    )

    state = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()

    assert state["traffic_light"] == "green"
    assert state["last_decision"] == "allow"
    assert state["last_decision_label"] == "Erlaubt"
    assert state["required_permission"] == "project.user_management.weight.change"
    assert state["authorization_evidence_count"] == 1
    assert state["last_successful_authorization_evidence"]["message_id"] == runtime.emitter.messages[-1].message_id
    assert state["can_undo"] is True
    assert state["can_redo"] is False
    assert state["weight_used_for_decision"] is False
    assert state["persisted"] is False

    overview = ZCockpitProjectLeadOverview(
        manager,
        messages=runtime.emitter.messages,
        user_management_runtime=runtime,
    ).state()
    assert overview["user_management_commands"]["last_decision"] == "allow"
    assert overview["summary"]["user_management_command_can_undo"] is True
    assert overview["summary"]["user_management_authorization_evidence_count"] == 1


def test_z_cockpit_command_diagnostics_show_denial_without_success_evidence():
    manager, administrator, target, runtime = _runtime(allow=False)

    with pytest.raises(PermissionError, match="not_granted"):
        runtime.changes.change_user_weight(
            target.user_id,
            400,
            command_context=_context(administrator.user_id),
        )

    state = ZCockpitUserManagementCommandDiagnosticsView(runtime).state()
    assert state["traffic_light"] == "yellow"
    assert state["attention_required"] is True
    assert state["last_decision"] == "not_granted"
    assert state["last_decision_label"] == "Recht nicht erteilt"
    assert state["authorization_evidence_count"] == 0
    assert state["last_successful_authorization_evidence"] is None
    assert state["can_undo"] is False
    assert manager.sync_log.entries == []

    overview = ZCockpitProjectLeadOverview(
        manager,
        user_management_runtime=runtime,
    ).state()
    assert overview["user_management_commands"]["attention_required"] is True
    assert "Der letzte Benutzerverwaltungs-Command wurde durch die Autorisierung abgewiesen." in overview["attention_reasons"]
