from datetime import datetime, timezone
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import (
    ProjectOSAuthorizationEvaluator,
    ProjectOSPermissionAssignment,
    ProjectOSUserProfile,
)
from .projectos_permission_revocation import ProjectOSPermissionRevocation
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService
from .projectos_user_management_command_context import ProjectOSUserManagementCommandContext
from .projectos_user_management_persistence import (
    ProjectOSUserManagementState,
    USER_MANAGEMENT_PERSISTENCE_VERSION,
)
from .projectos_user_management_runtime import build_projectos_user_management_runtime


def _context(actor_user_id: str) -> ProjectOSUserManagementCommandContext:
    return ProjectOSUserManagementCommandContext(
        actor_user_id=actor_user_id,
        correlation_id=str(uuid4()),
    )


def test_permission_revocation_is_timezone_aware_and_effective_from_revoked_at():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Engineering")
    actor = ProjectOSUserProfile("Administration")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    revocation = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=assignment.scope,
        revoked_at="2026-08-09T12:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Zugriff nicht mehr erforderlich",
        source_reference="IAM-42",
    )

    assert revocation.is_effective(datetime(2026, 8, 9, 11, 59, tzinfo=timezone.utc)) is False
    assert revocation.is_effective(datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)) is True
    assert revocation.as_dict()["source_reference"] == "IAM-42"

    with pytest.raises(ValueError, match="revocation reason"):
        ProjectOSPermissionRevocation(
            assignment_id=assignment.assignment_id,
            project_id=project_id,
            user_id=user.user_id,
            scope=assignment.scope,
            revoked_at="2026-08-09T12:00:00+00:00",
            revoked_by_user_id=actor.user_id,
            reason=" ",
        )


def test_authorization_keeps_assignment_before_revocation_and_blocks_it_afterwards():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Engineering")
    actor = ProjectOSUserProfile("Administration")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    revocation = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=assignment.scope,
        revoked_at="2026-08-09T12:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Projektphase beendet",
    )
    evaluator = ProjectOSAuthorizationEvaluator([assignment], [revocation])

    before = evaluator.evaluate(
        user,
        "project.read",
        at=datetime(2026, 8, 9, 11, 59, tzinfo=timezone.utc),
    )
    after = evaluator.evaluate(
        user,
        "project.read",
        at=datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc),
    )

    assert before["decision"] == "allow"
    assert before["revocation_count"] == 0
    assert after["decision"] == "not_granted"
    assert after["revocation_count"] == 1
    assert after["revoked_assignments"][0]["assignment"]["assignment_id"] == assignment.assignment_id
    assert after["revoked_assignments"][0]["revocation"]["revocation_id"] == revocation.revocation_id


def test_user_management_v1_remains_readable_and_migrates_in_memory_to_v2():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Altbestand")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    legacy = ProjectOSUserManagementState(
        project_id=project_id,
        users=(user,),
        permission_assignments=(assignment,),
    ).as_dict()
    legacy["version"] = 1
    legacy.pop("permission_revocations")

    restored = ProjectOSUserManagementState.from_dict(legacy)

    assert restored.permission_revocations == ()
    assert restored.as_dict()["version"] == USER_MANAGEMENT_PERSISTENCE_VERSION == 2


def test_persistence_rejects_mismatched_or_duplicate_permission_revocation():
    project_id = str(uuid4())
    user = ProjectOSUserProfile("Engineering")
    actor = ProjectOSUserProfile("Administration")
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    revocation = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=assignment.scope,
        revoked_at="2026-08-09T12:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Beendet",
    )
    duplicate = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope=assignment.scope,
        revoked_at="2026-08-09T13:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Nochmals beendet",
    )

    with pytest.raises(ValueError, match="already revoked"):
        ProjectOSUserManagementState(
            project_id=project_id,
            users=(user, actor),
            permission_assignments=(assignment,),
            permission_revocations=(revocation, duplicate),
        )

    wrong_scope = ProjectOSPermissionRevocation(
        assignment_id=assignment.assignment_id,
        project_id=project_id,
        user_id=user.user_id,
        scope="project:other",
        revoked_at="2026-08-09T12:00:00+00:00",
        revoked_by_user_id=actor.user_id,
        reason="Falscher Scope",
    )
    with pytest.raises(ValueError, match="scope does not match"):
        ProjectOSUserManagementState(
            project_id=project_id,
            users=(user, actor),
            permission_assignments=(assignment,),
            permission_revocations=(wrong_scope,),
        )


def test_secured_revocation_command_keeps_assignment_and_emits_trace_and_audit():
    manager = DinEditorProjectManager()
    bootstrap = ProjectOSUserManagementChangeService(manager)
    admin = bootstrap.create_user("Administration")
    target = bootstrap.create_user("Engineering")
    bootstrap.command_assign_permission(
        user_id=admin.user_id,
        permission="project.user_management.permission.revoke",
        source_type="direct",
        effect="allow",
    )
    assignment = bootstrap.command_assign_permission(
        user_id=target.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    runtime = build_projectos_user_management_runtime(manager)
    context = _context(admin.user_id)

    revocation = runtime.changes.command_revoke_permission(
        assignment_id=assignment.assignment_id,
        revoked_at="2026-08-09T12:00:00+00:00",
        revoked_by_user_id=admin.user_id,
        reason="Projektzugriff beendet",
        source_reference="CHANGE-17",
        command_context=context,
    )

    assert len(manager.user_management.permission_assignments) == 2
    assert len(manager.user_management.permission_revocations) == 1
    assert manager.user_management.permission_revocations[0] == revocation
    assert runtime.emitter.traces[-1].operation == "permission_revoked"
    assert runtime.emitter.traces[-1].reference == revocation.revocation_id
    assert runtime.emitter.traces[-1].actor_user_id == admin.user_id
    assert manager.sync_log.entries[-1]["action"] == "permission_revoked"
    assert manager.sync_log.entries[-1]["command_id"] == context.command_id
    assert runtime.emitter.command_history.latest().reversible is False

    with pytest.raises(ValueError, match="already revoked"):
        runtime.changes.command_revoke_permission(
            assignment_id=assignment.assignment_id,
            revoked_at="2026-08-09T13:00:00+00:00",
            revoked_by_user_id=admin.user_id,
            reason="Doppelter Widerruf",
            command_context=_context(admin.user_id),
        )
