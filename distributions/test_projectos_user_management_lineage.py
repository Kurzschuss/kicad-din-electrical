from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_policy import ProjectOSUserManagementCommandPolicy
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_user_management_lineage import ZCockpitUserManagementLineageView


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def test_permission_regrant_creates_new_assignment_and_preserves_history(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    target = bootstrap.create_user("Ziel")
    bootstrap.command_assign_permission(
        user_id=actor.user_id,
        permission="project.user_management.permission.regrant",
        source_type="direct",
        effect="allow",
    )
    original = bootstrap.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        risk_class="high",
        source_reference="GRANT-1",
    )
    revocation = bootstrap.command_revoke_permission(
        assignment_id=original.assignment_id,
        revoked_at="2026-08-09T10:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Altzuweisung beendet",
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(actor.user_id)

    successor = runtime.changes.command_regrant_permission(
        predecessor_assignment_id=original.assignment_id,
        regranted_at="2026-08-09T10:01:00+00:00",
        regranted_by_user_id=actor.user_id,
        source_reference="REGRANT-1",
        command_context=context,
    )

    assert successor.assignment_id != original.assignment_id
    assert len(manager.user_management.permission_assignments) == 3
    assert original in manager.user_management.permission_assignments
    assert revocation in manager.user_management.permission_revocations
    assert successor.metadata["lineage_type"] == "permission_regrant"
    assert successor.metadata["predecessor_assignment_id"] == original.assignment_id
    assert successor.metadata["predecessor_revocation_id"] == revocation.revocation_id
    assert successor.metadata["regranted_by_user_id"] == actor.user_id
    assert runtime.emitter.traces[-1].operation == "permission_regranted"
    assert runtime.emitter.traces[-1].reference == successor.assignment_id
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.command_history.latest().reversible is False

    lineage = ZCockpitUserManagementLineageView(manager).state()
    assert lineage["traffic_light"] == "green"
    assert lineage["permission_regrant_count"] == 1
    assert lineage["permission_regrant_chains"][0]["valid"] is True

    saved = manager.save(tmp_path / "regrant-lineage.json")
    loaded = DinEditorProjectManager()
    loaded.load(saved)
    loaded_lineage = ZCockpitUserManagementLineageView(loaded).state()
    assert loaded_lineage["permission_regrant_count"] == 1
    assert loaded_lineage["permission_regrant_chains"][0]["successor_assignment"]["assignment_id"] == successor.assignment_id


def test_permission_regrant_requires_effective_revocation_and_single_successor():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    target = bootstrap.create_user("Ziel")
    bootstrap.command_assign_permission(
        user_id=actor.user_id,
        permission="project.user_management.permission.regrant",
        source_type="direct",
        effect="allow",
    )
    original = bootstrap.command_assign_permission(
        user_id=target.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
    )
    bootstrap.command_revoke_permission(
        assignment_id=original.assignment_id,
        revoked_at="2099-01-01T00:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Geplanter Widerruf",
    )
    runtime = build_projectos_user_management_runtime(manager)

    with pytest.raises(ValueError, match="effective predecessor revocation"):
        runtime.changes.command_regrant_permission(
            predecessor_assignment_id=original.assignment_id,
            regranted_at="2026-08-09T10:00:00+00:00",
            regranted_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )

    successor = runtime.changes.command_regrant_permission(
        predecessor_assignment_id=original.assignment_id,
        regranted_at="2099-01-01T00:00:00+00:00",
        regranted_by_user_id=actor.user_id,
        command_context=_context(actor.user_id),
    )
    assert successor.assignment_id != original.assignment_id

    with pytest.raises(ValueError, match="already has a regrant successor"):
        runtime.changes.command_regrant_permission(
            predecessor_assignment_id=original.assignment_id,
            regranted_at="2099-01-01T00:01:00+00:00",
            regranted_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )


def test_high_risk_role_reassignment_requires_approval_effective_termination(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Projektleitung")
    deputy = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Freigabe")
    bootstrap.command_assign_permission(
        user_id=actor.user_id,
        permission="project.user_management.role.reassign",
        source_type="direct",
        effect="allow",
    )
    original = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=actor.user_id,
        source_reference="ROLE-OLD",
    )
    termination = bootstrap.command_terminate_project_role_assignment(
        role_assignment_id=original.role_assignment_id,
        ended_at="2026-08-09T10:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Alte Stellvertretung beendet",
    )
    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_risk_class_map={"deputy": "high"},
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)

    before = manager.user_management.as_dict()
    with pytest.raises(ValueError, match="approval-effective predecessor termination"):
        runtime.changes.command_reassign_project_role(
            predecessor_role_assignment_id=original.role_assignment_id,
            reassigned_at="2026-08-09T10:01:00+00:00",
            reassigned_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )
    assert manager.user_management.as_dict() == before

    request = bootstrap.command_request_approval(
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=actor.user_id,
        risk_class="high",
        requested_at="2026-08-09T10:00:10+00:00",
    )
    bootstrap.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T10:00:20+00:00",
    )
    context = _context(actor.user_id)
    successor = runtime.changes.command_reassign_project_role(
        predecessor_role_assignment_id=original.role_assignment_id,
        reassigned_at="2026-08-09T10:01:00+00:00",
        reassigned_by_user_id=actor.user_id,
        source_reference="ROLE-NEW",
        command_context=context,
    )

    assert successor.role_assignment_id != original.role_assignment_id
    assert original in manager.user_management.project_roles
    assert termination in manager.user_management.role_assignment_terminations
    assert successor.metadata["lineage_type"] == "project_role_reassignment"
    assert successor.metadata["predecessor_role_assignment_id"] == original.role_assignment_id
    assert successor.metadata["predecessor_termination_id"] == termination.termination_id
    assert successor.metadata["reassigned_by_user_id"] == actor.user_id
    assert runtime.emitter.traces[-1].operation == "project_role_reassigned"
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id

    lineage = ZCockpitUserManagementLineageView(manager).state()
    assert lineage["role_reassignment_count"] == 1
    assert lineage["role_reassignment_chains"][0]["valid"] is True

    saved = manager.save(tmp_path / "role-reassignment-lineage.json")
    loaded = DinEditorProjectManager()
    loaded.load(saved)
    loaded_lineage = ZCockpitUserManagementLineageView(loaded).state()
    assert loaded_lineage["role_reassignment_count"] == 1
    assert loaded_lineage["role_reassignment_chains"][0]["successor_role_assignment"]["role_assignment_id"] == successor.role_assignment_id


def test_role_reassignment_fails_closed_without_risk_configuration_or_permission():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Projektleitung")
    deputy = bootstrap.create_user("Stellvertretung")
    original = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=actor.user_id,
    )
    bootstrap.command_terminate_project_role_assignment(
        role_assignment_id=original.role_assignment_id,
        ended_at="2026-08-09T10:00:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Beendet",
    )
    runtime = build_projectos_user_management_runtime(manager)

    before = manager.user_management.as_dict()
    with pytest.raises(ValueError, match="approval-effective predecessor termination"):
        runtime.changes.command_reassign_project_role(
            predecessor_role_assignment_id=original.role_assignment_id,
            reassigned_at="2026-08-09T10:01:00+00:00",
            reassigned_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )
    assert manager.user_management.as_dict() == before

    configured = build_projectos_user_management_runtime(
        manager,
        policy=ProjectOSUserManagementCommandPolicy.configured(role_risk_class_map={"deputy": "low"}),
    )
    with pytest.raises(PermissionError, match=r"project_role_reassigned \(not_granted\)"):
        configured.changes.command_reassign_project_role(
            predecessor_role_assignment_id=original.role_assignment_id,
            reassigned_at="2026-08-09T10:01:00+00:00",
            reassigned_by_user_id=actor.user_id,
            command_context=_context(actor.user_id),
        )
    assert manager.user_management.as_dict() == before
