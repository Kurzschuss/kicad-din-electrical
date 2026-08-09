from datetime import datetime, timezone
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSAuthorizationEvaluator
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_command_policy import ProjectOSUserManagementCommandPolicy
from .projectos_user_management_persistence import ProjectOSUserManagementState
from .projectos_user_management_runtime import build_projectos_user_management_runtime
from .z_cockpit_authorization import ZCockpitAuthorizationView
from .z_cockpit_user_lifecycle import ZCockpitUserLifecycleView
from .z_cockpit_user_management_persistence import ZCockpitUserManagementPersistenceView


BEFORE = datetime(2026, 8, 9, 11, 59, tzinfo=timezone.utc)
AFTER = datetime(2026, 8, 9, 12, 1, tzinfo=timezone.utc)


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(actor_user_id=actor_user_id, correlation_id=str(uuid4()))


def test_user_deactivation_is_time_effective_and_preserves_direct_permission_history():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    assignment = bootstrap.command_assign_permission(
        user_id=user.user_id,
        permission="project.release",
        source_type="direct",
        effect="allow",
    )
    deactivation = bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
        source_reference="OFF-42",
    )
    evaluator = ProjectOSAuthorizationEvaluator(
        manager.user_management.permission_assignments,
        manager.user_management.permission_revocations,
        manager.user_management.user_deactivations,
    )

    before = evaluator.evaluate(user, "project.release", at=BEFORE)
    after = evaluator.evaluate(user, "project.release", at=AFTER)

    assert before["decision"] == "allow"
    assert before["allowed"] is True
    assert after["decision"] == "user_deactivated"
    assert after["allowed"] is False
    assert after["user_deactivation"]["deactivation_id"] == deactivation.deactivation_id
    assert assignment in manager.user_management.permission_assignments
    assert user in manager.user_management.users

    cockpit = ZCockpitAuthorizationView(
        user,
        manager.user_management.permission_assignments,
        manager.user_management.permission_revocations,
        manager.user_management.user_deactivations,
    ).state("project.release", at=AFTER)
    assert cockpit["decision"] == "user_deactivated"
    assert cockpit["user_deactivated"] is True
    assert cockpit["active_source_count"] == 0
    assert cockpit["inactive_source_count"] == 1


def test_secured_user_deactivation_blocks_future_actor_commands_without_side_effects():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    security = bootstrap.create_user("Security")
    worker = bootstrap.create_user("Worker")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=security.user_id,
        permission="project.user_management.user.deactivate",
        source_type="direct", effect="allow",
    )
    bootstrap.command_assign_permission(
        user_id=worker.user_id,
        permission="project.user_management.weight.change",
        source_type="direct", effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(security.user_id)

    deactivation = runtime.changes.command_deactivate_user(
        user_id=worker.user_id,
        deactivated_at="2026-08-09T00:00:00+00:00",
        deactivated_by_user_id=security.user_id,
        reason="Zugang beendet",
        command_context=context,
    )

    assert worker in manager.user_management.users
    assert manager.user_management.user_deactivations == (deactivation,)
    assert runtime.emitter.traces[-1].operation == "user_deactivated"
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.command_history.latest().reversible is False

    before_state = manager.user_management.as_dict()
    audit_count = len(manager.sync_log.entries)
    trace_count = len(runtime.emitter.traces)
    history_count = len(runtime.emitter.command_history.all())
    decision = runtime.authorization.evaluate("user_weight_changed", _context(worker.user_id), at=AFTER)
    assert decision["decision"] == "user_deactivated"
    assert decision["allowed"] is False
    assert decision["role_derived_assignment_count"] == 0

    with pytest.raises(PermissionError, match="user_deactivated"):
        runtime.changes.change_user_weight(target.user_id, 500, command_context=_context(worker.user_id))
    assert manager.user_management.as_dict() == before_state
    assert next(item.weight for item in manager.user_management.users if item.user_id == target.user_id) == 100
    assert len(manager.sync_log.entries) == audit_count
    assert len(runtime.emitter.traces) == trace_count
    assert len(runtime.emitter.command_history.all()) == history_count


def test_deactivated_role_holder_loses_role_derived_command_rights():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    security = bootstrap.create_user("Security")
    deputy = bootstrap.create_user("Stellvertretung")
    target = bootstrap.create_user("Ziel", weight=100)
    bootstrap.command_assign_permission(
        user_id=security.user_id,
        permission="project.user_management.user.deactivate",
        source_type="direct", effect="allow",
    )
    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=security.user_id,
    )
    bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="absence",
        triggered_by_user_id=security.user_id,
    )
    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_permission_map={"deputy": ["project.user_management.weight.change"]},
        role_risk_class_map={"deputy": "low"},
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)
    assert runtime.authorization.evaluate("user_weight_changed", _context(deputy.user_id), at=BEFORE)["allowed"] is True

    runtime.changes.command_deactivate_user(
        user_id=deputy.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=security.user_id,
        reason="Offboarding",
        command_context=_context(security.user_id),
    )
    decision = runtime.authorization.evaluate("user_weight_changed", _context(deputy.user_id), at=AFTER)
    assert decision["decision"] == "user_deactivated"
    assert decision["allowed"] is False
    assert decision["role_derived_assignment_count"] == 0
    assert role in manager.user_management.project_roles
    assert manager.user_management.activations
    assert next(item.weight for item in manager.user_management.users if item.user_id == target.user_id) == 100


def test_secured_deactivation_actor_must_match_command_actor():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    actor = bootstrap.create_user("Security")
    other = bootstrap.create_user("Anderer")
    user = bootstrap.create_user("Ziel")
    bootstrap.command_assign_permission(
        user_id=actor.user_id,
        permission="project.user_management.user.deactivate",
        source_type="direct", effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)
    before = manager.user_management.as_dict()

    with pytest.raises(ValueError, match="deactivated_by_user_id must match command actor"):
        runtime.changes.command_deactivate_user(
            user_id=user.user_id,
            deactivated_at="2026-08-09T12:00:00+00:00",
            deactivated_by_user_id=other.user_id,
            reason="Falscher Akteur",
            command_context=_context(actor.user_id),
        )
    assert manager.user_management.as_dict() == before
    assert runtime.emitter.traces == []
    assert manager.sync_log.entries == []


def test_user_deactivation_persistence_v3_and_legacy_v2_compatibility(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    deactivation = bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
    )
    path = manager.save(tmp_path / "user-deactivation.json")
    loaded = DinEditorProjectManager(); loaded.load(path)

    assert loaded.user_management.as_dict()["version"] == 3
    assert loaded.user_management.users[1].user_id == user.user_id
    assert loaded.user_management.user_deactivations[0].deactivation_id == deactivation.deactivation_id
    persistence = ZCockpitUserManagementPersistenceView(loaded).state()
    assert persistence["persisted_counts"]["user_deactivations"] == 1
    lifecycle = ZCockpitUserLifecycleView(loaded).state(at=AFTER)
    assert lifecycle["deactivated_user_count"] == 1
    assert lifecycle["deactivated_users"][0]["user"]["user_id"] == user.user_id

    legacy = manager.user_management.as_dict()
    legacy["version"] = 2
    legacy.pop("user_deactivations", None)
    migrated = ProjectOSUserManagementState.from_dict(legacy)
    assert migrated.user_deactivations == ()
    assert migrated.as_dict()["version"] == 3


def test_duplicate_user_deactivation_is_rejected_without_deleting_identity():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=admin.user_id,
        reason="Erste Deaktivierung",
    )
    with pytest.raises(ValueError, match="user already deactivated"):
        bootstrap.command_deactivate_user(
            user_id=user.user_id,
            deactivated_at="2026-08-09T13:00:00+00:00",
            deactivated_by_user_id=admin.user_id,
            reason="Doppelte Deaktivierung",
        )
    assert user in manager.user_management.users
