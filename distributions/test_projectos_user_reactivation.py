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
from .z_cockpit_approved_role_activation import ZCockpitApprovedRoleActivationView
from .z_cockpit_authorization import ZCockpitAuthorizationView
from .z_cockpit_user_lifecycle import ZCockpitUserLifecycleView
from .z_cockpit_user_management_persistence import ZCockpitUserManagementPersistenceView


T0 = datetime(2026, 8, 9, 10, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 8, 9, 11, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)
T3 = datetime(2026, 8, 9, 13, 0, tzinfo=timezone.utc)


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(actor_user_id=actor_user_id, correlation_id=str(uuid4()))


def test_direct_permission_returns_after_reactivation_of_same_user_id():
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
        deactivated_at=T1.isoformat(),
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
    )
    reactivation = bootstrap.command_reactivate_user(
        user_id=user.user_id,
        reactivated_at=T2.isoformat(),
        reactivated_by_user_id=admin.user_id,
        reason="Rückkehr",
    )
    evaluator = ProjectOSAuthorizationEvaluator(
        manager.user_management.permission_assignments,
        manager.user_management.permission_revocations,
        manager.user_management.user_deactivations,
        manager.user_management.user_reactivations,
    )

    before = evaluator.evaluate(user, "project.release", at=T0)
    during = evaluator.evaluate(user, "project.release", at=datetime(2026, 8, 9, 11, 30, tzinfo=timezone.utc))
    after = evaluator.evaluate(user, "project.release", at=T3)

    assert before["decision"] == "allow"
    assert during["decision"] == "user_deactivated"
    assert after["decision"] == "allow"
    assert after["user_lifecycle_status"] == "active"
    assert after["user_reactivation"]["reactivation_id"] == reactivation.reactivation_id
    assert after["user_deactivation"] is None
    assert user.user_id == deactivation.user_id == reactivation.user_id
    assert assignment in manager.user_management.permission_assignments

    cockpit = ZCockpitAuthorizationView(
        user,
        manager.user_management.permission_assignments,
        manager.user_management.permission_revocations,
        manager.user_management.user_deactivations,
        manager.user_management.user_reactivations,
    ).state("project.release", at=T3)
    assert cockpit["allowed"] is True
    assert cockpit["user_lifecycle_status"] == "active"
    assert cockpit["user_reactivation"]["reactivation_id"] == reactivation.reactivation_id


def test_role_derived_permission_returns_from_same_historical_role_after_reactivation():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    deputy = bootstrap.create_user("Stellvertretung")
    role = bootstrap.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        assigned_by_user_id=admin.user_id,
    )
    activation = bootstrap.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="absence",
        triggered_by_user_id=admin.user_id,
    )
    bootstrap.command_deactivate_user(
        user_id=deputy.user_id,
        deactivated_at=T1.isoformat(),
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
    )
    bootstrap.command_reactivate_user(
        user_id=deputy.user_id,
        reactivated_at=T2.isoformat(),
        reactivated_by_user_id=admin.user_id,
        reason="Rückkehr",
    )
    policy = ProjectOSUserManagementCommandPolicy.configured(
        role_permission_map={"deputy": ["project.user_management.weight.change"]},
        role_risk_class_map={"deputy": "low"},
    )
    runtime = build_projectos_user_management_runtime(manager, policy=policy)

    during = runtime.authorization.evaluate(
        "user_weight_changed",
        _context(deputy.user_id),
        at=datetime(2026, 8, 9, 11, 30, tzinfo=timezone.utc),
    )
    after = runtime.authorization.evaluate("user_weight_changed", _context(deputy.user_id), at=T3)

    assert during["decision"] == "user_deactivated"
    assert after["decision"] == "allow"
    assert after["role_derived_assignment_count"] == 1
    assert after["user_lifecycle_status"] == "active"
    assert role in manager.user_management.project_roles
    assert activation in manager.user_management.activations

    cockpit = ZCockpitApprovedRoleActivationView(
        project_id=manager.project_id,
        user=deputy,
        roles=manager.user_management.project_roles,
        activations=manager.user_management.activations,
        permission_map={"deputy": ["project.user_management.weight.change"]},
        risk_class_map={"deputy": "low"},
        user_deactivations=manager.user_management.user_deactivations,
        user_reactivations=manager.user_management.user_reactivations,
    ).state(at=T3)
    assert cockpit["user_lifecycle_status"] == "active"
    assert cockpit["rights"][0]["allowed"] is True


def test_multiple_user_lifecycle_cycles_preserve_same_identity_and_chronology():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    d1 = bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at="2026-08-09T10:00:00+00:00",
        deactivated_by_user_id=admin.user_id,
        reason="Pause 1",
    )
    r1 = bootstrap.command_reactivate_user(
        user_id=user.user_id,
        reactivated_at="2026-08-09T11:00:00+00:00",
        reactivated_by_user_id=admin.user_id,
        reason="Rückkehr 1",
    )
    d2 = bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at="2026-08-09T12:00:00+00:00",
        deactivated_by_user_id=admin.user_id,
        reason="Pause 2",
    )
    r2 = bootstrap.command_reactivate_user(
        user_id=user.user_id,
        reactivated_at="2026-08-09T13:00:00+00:00",
        reactivated_by_user_id=admin.user_id,
        reason="Rückkehr 2",
    )

    lifecycle = ZCockpitUserLifecycleView(manager).state(at=datetime(2026, 8, 9, 14, 0, tzinfo=timezone.utc))
    row = next(item for item in lifecycle["active_users"] if item["user"]["user_id"] == user.user_id)
    assert row["event_count"] == 4
    assert [item["event_type"] for item in row["event_history"]] == [
        "deactivated", "reactivated", "deactivated", "reactivated"
    ]
    assert row["latest_event"]["reactivation_id"] == r2.reactivation_id
    assert {d1.user_id, r1.user_id, d2.user_id, r2.user_id} == {user.user_id}

    with pytest.raises(ValueError, match="cannot reactivate an active user"):
        bootstrap.command_reactivate_user(
            user_id=user.user_id,
            reactivated_at="2026-08-09T14:00:00+00:00",
            reactivated_by_user_id=admin.user_id,
            reason="Ungültige doppelte Reaktivierung",
        )


def test_user_lifecycle_rejects_equal_timestamp_and_invalid_sequence():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at=T1.isoformat(),
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
    )
    with pytest.raises(ValueError, match="distinct timestamps"):
        bootstrap.command_reactivate_user(
            user_id=user.user_id,
            reactivated_at=T1.isoformat(),
            reactivated_by_user_id=admin.user_id,
            reason="Gleicher Zeitpunkt",
        )

    manager2 = DinEditorProjectManager()
    bootstrap2 = ProjectOSUserManagementChangeService(manager2)
    admin2 = bootstrap2.create_user("Admin")
    user2 = bootstrap2.create_user("Benutzer")
    with pytest.raises(ValueError, match="cannot reactivate an active user"):
        bootstrap2.command_reactivate_user(
            user_id=user2.user_id,
            reactivated_at=T2.isoformat(),
            reactivated_by_user_id=admin2.user_id,
            reason="Ohne vorherige Deaktivierung",
        )


def test_secured_reactivation_requires_right_and_matching_actor_and_creates_trace():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    security = bootstrap.create_user("Security")
    other = bootstrap.create_user("Anderer")
    user = bootstrap.create_user("Benutzer")
    bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at=T1.isoformat(),
        deactivated_by_user_id=security.user_id,
        reason="Offboarding",
    )
    runtime = build_projectos_user_management_runtime(manager)
    before = manager.user_management.as_dict()

    with pytest.raises(PermissionError, match="user_reactivated \(not_granted\)"):
        runtime.changes.command_reactivate_user(
            user_id=user.user_id,
            reactivated_at=T2.isoformat(),
            reactivated_by_user_id=security.user_id,
            reason="Rückkehr",
            command_context=_context(security.user_id),
        )
    assert manager.user_management.as_dict() == before
    assert runtime.emitter.traces == []

    bootstrap.command_assign_permission(
        user_id=security.user_id,
        permission="project.user_management.user.reactivate",
        source_type="direct",
        effect="allow",
    )
    with pytest.raises(ValueError, match="reactivated_by_user_id must match command actor"):
        runtime.changes.command_reactivate_user(
            user_id=user.user_id,
            reactivated_at=T2.isoformat(),
            reactivated_by_user_id=other.user_id,
            reason="Falscher Akteur",
            command_context=_context(security.user_id),
        )

    context = _context(security.user_id)
    reactivation = runtime.changes.command_reactivate_user(
        user_id=user.user_id,
        reactivated_at=T2.isoformat(),
        reactivated_by_user_id=security.user_id,
        reason="Rückkehr",
        command_context=context,
    )
    assert reactivation.user_id == user.user_id
    assert runtime.emitter.traces[-1].operation == "user_reactivated"
    assert runtime.emitter.traces[-1].reference == reactivation.reactivation_id
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.command_history.latest().reversible is False


def test_user_reactivation_persistence_v4_and_legacy_v3_compatibility(tmp_path):
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Admin")
    user = bootstrap.create_user("Benutzer")
    deactivation = bootstrap.command_deactivate_user(
        user_id=user.user_id,
        deactivated_at=T1.isoformat(),
        deactivated_by_user_id=admin.user_id,
        reason="Offboarding",
    )
    reactivation = bootstrap.command_reactivate_user(
        user_id=user.user_id,
        reactivated_at=T2.isoformat(),
        reactivated_by_user_id=admin.user_id,
        reason="Rückkehr",
    )
    path = manager.save(tmp_path / "user-reactivation.json")
    loaded = DinEditorProjectManager()
    loaded.load(path)

    assert loaded.user_management.as_dict()["version"] == 4
    assert loaded.user_management.users[1].user_id == user.user_id
    assert loaded.user_management.user_deactivations[0].deactivation_id == deactivation.deactivation_id
    assert loaded.user_management.user_reactivations[0].reactivation_id == reactivation.reactivation_id
    persistence = ZCockpitUserManagementPersistenceView(loaded).state()
    assert persistence["persisted_counts"]["user_deactivations"] == 1
    assert persistence["persisted_counts"]["user_reactivations"] == 1
    lifecycle = ZCockpitUserLifecycleView(loaded).state(at=T3)
    assert lifecycle["deactivated_user_count"] == 0
    row = next(item for item in lifecycle["active_users"] if item["user"]["user_id"] == user.user_id)
    assert row["latest_event_type"] == "reactivated"

    legacy = manager.user_management.as_dict()
    legacy["version"] = 3
    legacy.pop("user_reactivations", None)
    migrated = ProjectOSUserManagementState.from_dict(legacy)
    assert migrated.user_reactivations == ()
    assert migrated.as_dict()["version"] == 4
