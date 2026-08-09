from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorized_user_management_change_service import (
    ProjectOSAuthorizedUserManagementChangeService,
)
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_change_trace import ProjectOSUserManagementChangeTraceEmitter
from .projectos_user_management_command_authorization import (
    ProjectOSUserManagementCommandAuthorization,
)
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_undo_redo import ProjectOSUserManagementUndoRedoService

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


def _secured(
    manager: DinEditorProjectManager,
    *,
    command_permission_map=None,
    role_permission_map=None,
    role_risk_class_map=None,
):
    emitter = ProjectOSUserManagementChangeTraceEmitter(manager)
    authorization = ProjectOSUserManagementCommandAuthorization(
        manager,
        command_permission_map=command_permission_map or {
            "user_weight_changed": WEIGHT_CHANGE,
            "undo:user_weight_changed": WEIGHT_UNDO,
            "redo:user_weight_changed": WEIGHT_REDO,
        },
        role_permission_map=role_permission_map,
        role_risk_class_map=role_risk_class_map,
    )
    service = ProjectOSAuthorizedUserManagementChangeService(
        manager,
        authorization=authorization,
        on_change=emitter,
    )
    return emitter, authorization, service


def test_direct_allow_authorizes_weight_change_and_missing_context_fails_closed():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission=WEIGHT_CHANGE,
        source_type="direct",
        effect="allow",
    )
    emitter, _, service = _secured(manager)

    service.change_user_weight(target.user_id, 300, command_context=_context(administrator.user_id))

    assert _weight(manager, target.user_id) == 300
    assert service.last_authorization["decision"] == "allow"
    assert service.last_authorization["required_permission"] == WEIGHT_CHANGE
    assert service.last_authorization["weight_used_for_decision"] is False
    assert len(emitter.traces) == 1

    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())
    with pytest.raises(PermissionError, match="missing_command_context"):
        service.change_user_weight(target.user_id, 400)

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count


def test_deny_overrides_allow_and_user_weight_never_grants_permission():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator", weight=1000)
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission=WEIGHT_CHANGE,
        source_type="direct",
        effect="allow",
    )
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission=WEIGHT_CHANGE,
        source_type="blacklist",
        effect="deny",
        risk_class="critical",
    )
    emitter, authorization, service = _secured(manager)
    context = _context(administrator.user_id)

    decision = authorization.evaluate("user_weight_changed", context)
    assert decision["decision"] == "deny"
    assert decision["allowed"] is False
    assert decision["deny_precedence"] is True
    assert decision["weight_used_for_decision"] is False

    with pytest.raises(PermissionError, match="\(deny\)"):
        service.change_user_weight(target.user_id, 900, command_context=context)

    assert _weight(manager, target.user_id) == 100
    assert emitter.traces == []
    assert manager.sync_log.entries == []

    second_manager = DinEditorProjectManager()
    second_bootstrap = ProjectOSUserManagementChangeService(second_manager)
    heavy_user = second_bootstrap.create_user("Benutzer mit hoher Gewichtung", weight=1000)
    second_target = second_bootstrap.create_user("Ziel", weight=100)
    _, second_authorization, _ = _secured(second_manager)
    no_right = second_authorization.evaluate("user_weight_changed", _context(heavy_user.user_id))
    assert no_right["decision"] == "not_granted"
    assert no_right["allowed"] is False
    assert second_target.weight == 100


def test_undo_and_redo_use_distinct_configured_permissions():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    for permission in (WEIGHT_CHANGE, WEIGHT_UNDO, WEIGHT_REDO):
        bootstrap.command_assign_permission(
            user_id=administrator.user_id,
            permission=permission,
            source_type="direct",
            effect="allow",
        )
    emitter, _, service = _secured(manager)
    service.change_user_weight(target.user_id, 400, command_context=_context(administrator.user_id))
    undo_redo = ProjectOSUserManagementUndoRedoService(service)

    undo = undo_redo.undo_latest(actor_user_id=administrator.user_id)
    assert _weight(manager, target.user_id) == 100
    undo_record = emitter.command_history.get(undo.command_id)
    assert undo_record is not None
    assert undo_record.history_action == "undo"
    assert service.last_authorization["policy_key"] == "undo:user_weight_changed"
    assert service.last_authorization["required_permission"] == WEIGHT_UNDO

    redo = undo_redo.redo_latest(actor_user_id=administrator.user_id)
    assert _weight(manager, target.user_id) == 400
    redo_record = emitter.command_history.get(redo.command_id)
    assert redo_record is not None
    assert redo_record.history_action == "redo"
    assert service.last_authorization["policy_key"] == "redo:user_weight_changed"
    assert service.last_authorization["required_permission"] == WEIGHT_REDO


def test_missing_undo_permission_denies_without_domain_audit_or_history_change():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    administrator = bootstrap.create_user("Administrator")
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    bootstrap.command_assign_permission(
        user_id=administrator.user_id,
        permission=WEIGHT_CHANGE,
        source_type="direct",
        effect="allow",
    )
    emitter, _, service = _secured(manager)
    service.change_user_weight(target.user_id, 300, command_context=_context(administrator.user_id))
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())

    with pytest.raises(PermissionError, match="undo:user_weight_changed \(not_granted\)"):
        ProjectOSUserManagementUndoRedoService(service).undo_latest(
            actor_user_id=administrator.user_id
        )

    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count


def test_high_risk_role_permission_requires_existing_four_eyes_approval():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    principal = bootstrap.create_user("Projektleiter")
    deputy = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Freigeber")
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=principal.user_id,
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="vacation",
        triggered_by_user_id=principal.user_id,
    )
    request = bootstrap.command_request_approval(
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    emitter, authorization, service = _secured(
        manager,
        role_permission_map={"deputy": [WEIGHT_CHANGE]},
        role_risk_class_map={"deputy": "high"},
    )
    context = _context(deputy.user_id)

    pending = authorization.evaluate("user_weight_changed", context)
    assert pending["decision"] == "not_granted"
    assert pending["role_derived_assignment_count"] == 0
    with pytest.raises(PermissionError, match="not_granted"):
        service.change_user_weight(target.user_id, 250, command_context=context)

    bootstrap.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    approved_context = _context(deputy.user_id)
    approved = authorization.evaluate("user_weight_changed", approved_context)
    assert approved["decision"] == "allow"
    assert approved["role_derived_assignment_count"] == 1

    service.change_user_weight(target.user_id, 250, command_context=approved_context)
    assert _weight(manager, target.user_id) == 250
    assert len(emitter.traces) == 1

    bootstrap.command_assign_permission(
        user_id=deputy.user_id,
        permission=WEIGHT_CHANGE,
        source_type="deny",
        effect="deny",
        risk_class="critical",
    )
    denied = authorization.evaluate("user_weight_changed", _context(deputy.user_id))
    assert denied["decision"] == "deny"
    assert denied["allowed"] is False


def test_approved_deactivation_removes_role_permission_but_pending_deactivation_does_not():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    principal = bootstrap.create_user("Projektleiter")
    deputy = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Freigeber")
    target = bootstrap.create_user("Zielbenutzer", weight=100)
    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=principal.user_id,
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="vacation",
        triggered_by_user_id=principal.user_id,
    )
    activation_request = bootstrap.command_request_approval(
        action_type="activation",
        target_reference=activation.activation_id,
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:00:00+00:00",
    )
    bootstrap.command_record_approval(
        action_id=activation_request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T00:01:00+00:00",
    )
    deactivation = bootstrap.command_deactivate_project_role(
        activation_id=activation.activation_id,
        reason="principal_returned",
        ended_at="2026-08-09T00:02:00+00:00",
        triggered_by_user_id=principal.user_id,
    )
    emitter, authorization, service = _secured(
        manager,
        role_permission_map={"deputy": [WEIGHT_CHANGE]},
        role_risk_class_map={"deputy": "high"},
    )

    pending = authorization.evaluate("user_weight_changed", _context(deputy.user_id))
    assert pending["decision"] == "allow"
    assert pending["role_derived_assignment_count"] == 1
    service.change_user_weight(target.user_id, 200, command_context=_context(deputy.user_id))
    assert _weight(manager, target.user_id) == 200

    deactivation_request = bootstrap.command_request_approval(
        action_type="deactivation",
        target_reference=f"deactivation:{deactivation.deactivation_id}",
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T00:03:00+00:00",
    )
    bootstrap.command_record_approval(
        action_id=deactivation_request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T00:04:00+00:00",
    )

    ended = authorization.evaluate("user_weight_changed", _context(deputy.user_id))
    assert ended["decision"] == "not_granted"
    assert ended["role_derived_assignment_count"] == 0
    audit_count = len(manager.sync_log.entries)
    history_count = len(emitter.command_history.all())
    with pytest.raises(PermissionError, match="not_granted"):
        service.change_user_weight(target.user_id, 300, command_context=_context(deputy.user_id))

    assert _weight(manager, target.user_id) == 200
    assert len(manager.sync_log.entries) == audit_count
    assert len(emitter.command_history.all()) == history_count
