from datetime import datetime, timezone
from uuid import uuid4

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_role_assignment_termination_approval import ProjectOSApprovedRoleAssignmentTerminationEvaluator
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_policy import ProjectOSUserManagementCommandPolicy
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_role_compensation_plan import ZCockpitRoleCompensationPlanView


NOW = datetime(2026, 8, 9, 13, 30, tzinfo=timezone.utc)


def _setup(*, risk: str | None, grant_terminate: bool = True, approve_activation: bool = False):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Projektleitung")
    holder = bootstrap.create_user("Stellvertretung")
    approver = bootstrap.create_user("Freigabe")
    if grant_terminate:
        bootstrap.command_assign_permission(
            user_id=actor.user_id,
            permission="project.user_management.role.terminate",
            source_type="direct",
            effect="allow",
        )
    role = bootstrap.command_assign_project_role(
        user_id=holder.user_id,
        role_type="deputy",
        assigned_by_user_id=actor.user_id,
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="absence",
        triggered_by_user_id=actor.user_id,
    )
    if approve_activation:
        request = bootstrap.command_request_approval(
            action_type="activation",
            target_reference=activation.activation_id,
            requested_by_user_id=actor.user_id,
            risk_class="high",
            requested_at="2026-08-09T13:00:00+00:00",
        )
        bootstrap.command_record_approval(
            action_id=request.action_id,
            approver_user_id=approver.user_id,
            decision="approve",
            decided_at="2026-08-09T13:01:00+00:00",
        )
    risk_map = {} if risk is None else {"deputy": risk}
    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_permission_map={"deputy": ["project.release"]},
        role_risk_class_map=risk_map,
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)
    return manager, bootstrap, runtime, actor, holder, approver, role


def test_low_risk_plan_is_synchronous_and_read_only():
    manager, _, runtime, actor, _, _, role = _setup(risk="low")
    before = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)

    plan = ZCockpitRoleCompensationPlanView(runtime).state(
        role_assignment_id=role.role_assignment_id,
        actor_user_id=actor.user_id,
        at=NOW,
    )

    assert plan["actor_authorized"] is True
    assert plan["risk_class"] == "low"
    assert plan["second_person_required"] is False
    assert plan["synchronous_compensation_possible"] is True
    assert plan["requires_multistep_lifecycle"] is False
    assert plan["effective_role_permissions_at_risk"] == ["project.release"]
    assert plan["permission_impact_assessment_complete"] is True
    assert plan["next_action"] == "execute_termination"
    assert plan["generic_role_undo_enabled"] is False
    assert plan["traffic_light"] == "green"
    assert manager.user_management.as_dict() == before
    assert len(manager.sync_log.entries) == audit_count
    assert runtime.emitter.traces == []


def test_high_risk_plan_requires_multistep_approval_before_termination_effect():
    manager, _, runtime, actor, _, _, role = _setup(risk="high", approve_activation=True)
    before = manager.user_management.as_dict()

    plan = ZCockpitRoleCompensationPlanView(runtime).state(
        role_assignment_id=role.role_assignment_id,
        actor_user_id=actor.user_id,
        at=NOW,
    )

    assert plan["actor_authorized"] is True
    assert plan["risk_class"] == "high"
    assert plan["second_person_required"] is True
    assert plan["termination_present"] is False
    assert plan["synchronous_compensation_possible"] is False
    assert plan["requires_multistep_lifecycle"] is True
    assert plan["effective_role_permissions_at_risk"] == ["project.release"]
    assert plan["next_action"] == "create_termination_then_request_approval"
    assert plan["traffic_light"] == "yellow"
    assert manager.user_management.as_dict() == before


def test_pending_high_risk_termination_keeps_rights_at_risk_and_is_not_synchronous():
    manager, bootstrap, runtime, actor, _, _, role = _setup(risk="high", approve_activation=True)
    termination = bootstrap.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T13:10:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Offboarding",
    )
    bootstrap.command_request_approval(
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=actor.user_id,
        risk_class="high",
        requested_at="2026-08-09T13:11:00+00:00",
    )
    before = manager.user_management.as_dict()

    plan = ZCockpitRoleCompensationPlanView(runtime).state(
        role_assignment_id=role.role_assignment_id,
        actor_user_id=actor.user_id,
        at=NOW,
    )

    assert plan["termination_present"] is True
    assert plan["termination_approval_status"] == "pending_approval"
    assert plan["termination_effective"] is False
    assert plan["compensation_completed"] is False
    assert plan["synchronous_compensation_possible"] is False
    assert plan["effective_role_permissions_at_risk"] == ["project.release"]
    assert plan["next_action"] == "request_or_wait_for_approval"
    assert manager.user_management.as_dict() == before


def test_approved_high_risk_termination_is_completed_and_reassignment_is_possible():
    manager, bootstrap, runtime, actor, _, approver, role = _setup(risk="high", approve_activation=True)
    termination = bootstrap.command_terminate_project_role_assignment(
        role_assignment_id=role.role_assignment_id,
        ended_at="2026-08-09T13:10:00+00:00",
        ended_by_user_id=actor.user_id,
        reason="Offboarding",
    )
    request = bootstrap.command_request_approval(
        action_type="role_assignment_termination",
        target_reference=ProjectOSApprovedRoleAssignmentTerminationEvaluator.target_reference(termination.termination_id),
        requested_by_user_id=actor.user_id,
        risk_class="high",
        requested_at="2026-08-09T13:11:00+00:00",
    )
    bootstrap.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at="2026-08-09T13:12:00+00:00",
    )

    plan = ZCockpitRoleCompensationPlanView(runtime).state(
        role_assignment_id=role.role_assignment_id,
        actor_user_id=actor.user_id,
        at=NOW,
    )

    assert plan["termination_approval_status"] == "approved"
    assert plan["termination_effective"] is True
    assert plan["compensation_completed"] is True
    assert plan["reassignment_possible_now"] is True
    assert plan["effective_role_permissions_at_risk"] == ["project.release"]
    assert plan["next_action"] == "reassignment_possible"
    assert plan["generic_role_undo_enabled"] is False


def test_missing_risk_or_terminate_permission_fails_closed_without_mutation():
    manager, _, runtime, actor, _, _, role = _setup(risk=None)
    before = manager.user_management.as_dict()
    missing_risk = ZCockpitRoleCompensationPlanView(runtime).state(
        role_assignment_id=role.role_assignment_id,
        actor_user_id=actor.user_id,
        at=NOW,
    )
    assert missing_risk["actor_authorized"] is True
    assert missing_risk["configuration_required"] is True
    assert missing_risk["risk_class"] is None
    assert missing_risk["permission_impact_assessment_complete"] is False
    assert missing_risk["synchronous_compensation_possible"] is False
    assert missing_risk["next_action"] == "configure_role_risk"
    assert manager.user_management.as_dict() == before

    manager2, _, runtime2, actor2, _, _, role2 = _setup(risk="low", grant_terminate=False)
    before2 = manager2.user_management.as_dict()
    unauthorized = ZCockpitRoleCompensationPlanView(runtime2).state(
        role_assignment_id=role2.role_assignment_id,
        actor_user_id=actor2.user_id,
        at=NOW,
    )
    assert unauthorized["actor_authorized"] is False
    assert unauthorized["authorization"]["decision"] == "not_granted"
    assert unauthorized["synchronous_compensation_possible"] is False
    assert unauthorized["next_action"] == "obtain_role_terminate_permission"
    assert manager2.user_management.as_dict() == before2
