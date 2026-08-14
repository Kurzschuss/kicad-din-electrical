from dataclasses import replace
from datetime import datetime, timezone

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_offboarding_responsibility_diagnostics import (
    ProjectOSOffboardingResponsibilityDiagnostic,
)
from .projectos_role_approval import (
    ProjectOSRoleActionApproval,
    ProjectOSRoleActionApprovalRequest,
)
from .projectos_role_assignment_termination_approval import (
    ProjectOSApprovedRoleAssignmentTerminationEvaluator,
)
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .z_cockpit_offboarding_responsibility import ZCockpitOffboardingResponsibilityView


T10 = datetime(2026, 8, 9, 10, 0, tzinfo=timezone.utc)
T11 = datetime(2026, 8, 9, 11, 0, tzinfo=timezone.utc)
T12 = datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)


def test_deactivated_user_keeps_unresolved_permissions_and_roles_visible_read_only():
    manager = DinEditorProjectManager()
    changes = ProjectOSUserManagementChangeService(manager)
    admin = changes.create_user("Administration")
    user = changes.create_user("Engineering")
    permission = changes.command_assign_permission(
        user_id=user.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
        risk_class="high",
    )
    role = changes.command_assign_project_role(
        user_id=user.user_id,
        role_type="deputy",
        assigned_by_user_id=admin.user_id,
    )
    changes.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at=T11.isoformat(),
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding gestartet",
    )
    before_state = manager.user_management.as_dict()
    before_sync_log = list(manager.sync_log.entries)

    diagnostic = ProjectOSOffboardingResponsibilityDiagnostic(
        manager.user_management,
        role_risk_class_map={"deputy": "low"},
    ).state(user.user_id, at=T12)

    assert diagnostic["user_deactivated"] is True
    assert diagnostic["user_lifecycle_status"] == "deactivated"
    assert diagnostic["retained_permission_assignment_count"] == 1
    assert diagnostic["retained_permission_assignments"][0]["assignment"]["assignment_id"] == permission.assignment_id
    assert diagnostic["active_project_role_count"] == 1
    assert diagnostic["active_project_roles"][0]["role"]["role_assignment_id"] == role.role_assignment_id
    assert diagnostic["active_project_roles"][0]["termination_status"] == "not_started"
    assert diagnostic["resolution_required"] is True
    assert diagnostic["closure_evaluated"] is False
    assert diagnostic["handover_performed"] is False
    assert diagnostic["mutation_performed"] is False
    assert diagnostic["read_only"] is True
    assert manager.user_management.as_dict() == before_state
    assert manager.sync_log.entries == before_sync_log

    cockpit = ZCockpitOffboardingResponsibilityView(
        manager,
        role_risk_class_map={"deputy": "low"},
    ).state(user.user_id, at=T12)
    assert cockpit["attention_required"] is True
    assert cockpit["attention_count"] == 2
    assert cockpit["read_only"] is True
    assert manager.user_management.as_dict() == before_state
    assert manager.sync_log.entries == before_sync_log


def test_revoked_permission_and_effective_low_risk_role_termination_clear_diagnostic():
    manager = DinEditorProjectManager()
    changes = ProjectOSUserManagementChangeService(manager)
    admin = changes.create_user("Administration")
    user = changes.create_user("Engineering")
    permission = changes.command_assign_permission(
        user_id=user.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
    )
    role = changes.command_assign_project_role(
        user_id=user.user_id,
        role_type="deputy",
        assigned_by_user_id=admin.user_id,
    )
    changes.command_revoke_permission(
        assignment_id=permission.assignment_id,
        revoked_at=T10.isoformat(),
        revoked_by_user_id=admin.user_id,
        reason="Offboarding-Recht beendet",
    )
    changes.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at=T10.isoformat(),
        ended_by_user_id=admin.user_id,
        reason="Offboarding-Rolle beendet",
    )

    diagnostic = ProjectOSOffboardingResponsibilityDiagnostic(
        manager.user_management,
        role_risk_class_map={"deputy": "low"},
    ).state(user.user_id, at=T11)

    assert diagnostic["retained_permission_assignment_count"] == 0
    assert diagnostic["active_project_role_count"] == 0
    assert diagnostic["blocked_role_termination_count"] == 0
    assert diagnostic["pending_role_termination_post_review_count"] == 0
    assert diagnostic["attention_count"] == 0
    assert diagnostic["resolution_required"] is False
    assert diagnostic["closure_evaluated"] is False


def test_high_risk_role_termination_stays_open_until_external_approval():
    manager = DinEditorProjectManager()
    changes = ProjectOSUserManagementChangeService(manager)
    principal = changes.create_user("Projektleitung")
    user = changes.create_user("Stellvertretung")
    approver = changes.create_user("Freigabe")
    role = changes.command_assign_project_role(
        user_id=user.user_id,
        role_type="deputy",
        assigned_by_user_id=principal.user_id,
    )
    termination = changes.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at=T10.isoformat(),
        ended_by_user_id=principal.user_id,
        reason="High-Risk-Offboarding",
    )

    blocked = ProjectOSOffboardingResponsibilityDiagnostic(
        manager.user_management,
        role_risk_class_map={"deputy": "high"},
    ).state(user.user_id, at=T11)

    assert blocked["active_project_role_count"] == 1
    assert blocked["blocked_role_termination_count"] == 1
    assert blocked["active_project_roles"][0]["termination_status"] == "approval_missing"
    assert blocked["resolution_required"] is True

    request = ProjectOSRoleActionApprovalRequest(
        project_id=manager.project_id,
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(
            termination.termination_id
        ),
        requested_by_user_id=principal.user_id,
        risk_class="high",
        requested_at="2026-08-09T10:01:00+00:00",
    )
    approval = ProjectOSRoleActionApproval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T10:02:00+00:00",
    )
    approved_state = replace(
        manager.user_management,
        approval_requests=manager.user_management.approval_requests + (request,),
        approvals=manager.user_management.approvals + (approval,),
    )

    approved = ProjectOSOffboardingResponsibilityDiagnostic(
        approved_state,
        role_risk_class_map={"deputy": "high"},
    ).state(user.user_id, at=T11)

    assert approved["active_project_role_count"] == 0
    assert approved["blocked_role_termination_count"] == 0
    assert approved["resolution_required"] is False


def test_missing_role_risk_configuration_is_visible_and_fail_closed():
    manager = DinEditorProjectManager()
    changes = ProjectOSUserManagementChangeService(manager)
    admin = changes.create_user("Administration")
    user = changes.create_user("Engineering")
    changes.command_assign_project_role(
        user_id=user.user_id,
        role_type="deputy",
        assigned_by_user_id=admin.user_id,
    )

    diagnostic = ProjectOSOffboardingResponsibilityDiagnostic(
        manager.user_management,
        role_risk_class_map={},
    ).state(user.user_id, at=T12)

    assert diagnostic["active_project_role_count"] == 1
    assert diagnostic["role_risk_configuration_required"] is True
    assert diagnostic["active_project_roles"][0]["risk_class"] is None
    assert diagnostic["resolution_required"] is True
