from uuid import uuid4

import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSPermissionAssignment
from .projectos_user_management_change_service import ProjectOSUserManagementChangeService


def test_create_user_and_weight_change_mark_manager_dirty(tmp_path):
    manager = DinEditorProjectManager()
    manager.save(tmp_path / "project.json")
    service = ProjectOSUserManagementChangeService(manager)

    user = service.create_user("Projektleiter", weight=850)
    assert manager.has_unsaved_changes is True
    assert manager.user_management.users == (user,)

    manager.save()
    assert manager.has_unsaved_changes is False
    updated = service.change_user_weight(user.user_id, 900)
    assert updated.weight == 900
    assert manager.user_management.users[0].weight == 900
    assert manager.has_unsaved_changes is True
    assert manager.user_management.users[0].as_dict()["weight_affects_authorization"] is False


def test_invalid_change_is_atomic_and_does_not_call_hook(tmp_path):
    manager = DinEditorProjectManager()
    manager.save(tmp_path / "project.json")
    events = []
    service = ProjectOSUserManagementChangeService(manager, on_change=events.append)
    user = service.create_user("Projektleiter")
    manager.save()
    events.clear()
    before = manager.user_management.as_dict()

    invalid = ProjectOSPermissionAssignment(
        user_id=str(uuid4()),
        permission="project.release",
        source_type="direct",
        effect="allow",
    )
    with pytest.raises(ValueError, match="unknown user_id"):
        service.assign_permission(invalid)

    assert manager.user_management.as_dict() == before
    assert manager.has_unsaved_changes is False
    assert events == []
    assert manager.user_management.users[0].user_id == user.user_id


def test_successful_change_emits_transport_neutral_event():
    manager = DinEditorProjectManager()
    events = []
    service = ProjectOSUserManagementChangeService(manager, on_change=events.append)

    user = service.create_user("Stellvertretung", weight=700)
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    service.assign_permission(assignment)

    assert [event["operation"] for event in events] == ["user_created", "permission_assigned"]
    assert all(event["project_id"] == manager.project_id for event in events)
    assert all(event["dirty"] is True for event in events)
    assert manager.user_management.permission_assignments == (assignment,)


def test_duplicate_user_id_fails_before_manager_state_changes(tmp_path):
    manager = DinEditorProjectManager()
    service = ProjectOSUserManagementChangeService(manager)
    user_id = str(uuid4())
    service.create_user("Benutzer A", user_id=user_id)
    manager.save(tmp_path / "project.json")
    before = manager.user_management.as_dict()

    with pytest.raises(ValueError, match="user_id already exists"):
        service.create_user("Benutzer B", user_id=user_id)

    assert manager.user_management.as_dict() == before
    assert manager.has_unsaved_changes is False
