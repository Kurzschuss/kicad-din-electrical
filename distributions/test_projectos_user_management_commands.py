from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService


def _ts(hour: int) -> str:
    return datetime(2026, 8, 9, hour, 0, tzinfo=timezone.utc).isoformat()


def test_commands_build_role_activation_and_deactivation_from_existing_state():
    manager = DinEditorProjectManager()
    service = ProjectOSUserManagementChangeService(manager)
    lead = service.create_user("Projektleiter", weight=850)
    deputy = service.create_user("Stellvertretung", weight=700)

    role = service.command_assign_project_role(
        user_id=deputy.user_id,
        role_type="deputy",
        scope="project",
        assigned_by_user_id=lead.user_id,
        source_reference="command:test",
    )
    activation = service.command_activate_project_role(
        role_assignment_id=role.role_assignment_id,
        reason="vacation",
        valid_from=_ts(8),
        valid_until=_ts(18),
        triggered_by_user_id=lead.user_id,
        trigger_reference="vacation:2026-08-09",
    )
    deactivation = service.command_deactivate_project_role(
        activation_id=activation.activation_id,
        reason="principal_returned",
        ended_at=_ts(17),
        triggered_by_user_id=lead.user_id,
    )

    assert role.project_id == manager.project_id
    assert activation.project_id == manager.project_id
    assert activation.user_id == deputy.user_id
    assert activation.scope == role.scope
    assert deactivation.user_id == activation.user_id
    assert deactivation.scope == activation.scope
    assert manager.has_unsaved_changes is True


def test_commands_build_approval_and_post_review_from_ids():
    manager = DinEditorProjectManager()
    service = ProjectOSUserManagementChangeService(manager)
    requester = service.create_user("Projektleiter")
    approver = service.create_user("Vier-Augen-Pruefer")
    reviewer = service.create_user("Nachpruefer")

    request = service.command_request_approval(
        action_type="activation",
        target_reference=f"activation:{uuid4()}",
        requested_by_user_id=requester.user_id,
        risk_class="critical",
        requested_at=_ts(8),
        emergency=True,
        reason="Notfallvertretung",
    )
    approval = service.command_record_approval(
        action_id=request.action_id,
        approver_user_id=approver.user_id,
        decision="approve",
        decided_at=_ts(9),
    )
    review = service.command_complete_post_review(
        action_id=request.action_id,
        reviewer_user_id=reviewer.user_id,
        result="confirmed",
        reviewed_at=_ts(10),
        comment="Notfallhandlung bestätigt",
    )

    assert approval.action_id == request.action_id
    assert review.action_id == request.action_id
    assert review.reviewer_user_id == reviewer.user_id


def test_command_failure_is_atomic_for_unknown_role_assignment():
    manager = DinEditorProjectManager()
    events = []
    service = ProjectOSUserManagementChangeService(manager, on_change=events.append)
    service.create_user("Benutzer")
    before = manager.user_management.as_dict()
    events.clear()

    with pytest.raises(ValueError, match="unknown role_assignment_id"):
        service.command_activate_project_role(
            role_assignment_id=str(uuid4()),
            reason="manual",
            valid_from=_ts(8),
        )

    assert manager.user_management.as_dict() == before
    assert events == []


def test_permission_command_validates_user_before_commit():
    manager = DinEditorProjectManager()
    service = ProjectOSUserManagementChangeService(manager)
    before = manager.user_management.as_dict()

    with pytest.raises(ValueError, match="unknown user_id"):
        service.command_assign_permission(
            user_id=str(uuid4()),
            permission="project.release",
            source_type="direct",
            effect="allow",
        )

    assert manager.user_management.as_dict() == before


def test_production_modules_do_not_use_public_user_management_setter():
    root = Path(__file__).resolve().parent
    offenders = []
    for path in root.glob("*.py"):
        if path.name.startswith("test_") or path.name == "din_editor_project_manager.py":
            continue
        if ".set_user_management(" in path.read_text(encoding="utf-8"):
            offenders.append(path.name)

    assert offenders == []
