import json
from copy import deepcopy
from uuid import uuid4

import pytest

from .din_editor_project_bundle import DinProjectBundleError, recovery_path_for
from .din_editor_project_manager import DinEditorProjectManager
from .projectos_authorization import ProjectOSUserProfile
from .projectos_user_management_persistence import ProjectOSUserManagementState


def _state(project_id: str, name: str) -> ProjectOSUserManagementState:
    return ProjectOSUserManagementState(
        project_id=project_id,
        users=(ProjectOSUserProfile(display_name=name, weight=850),),
    )


def _manager_snapshot(manager: DinEditorProjectManager) -> dict:
    return {
        "project_id": manager.project_id,
        "path": str(manager.path) if manager.path is not None else None,
        "session": deepcopy(manager.session.state()),
        "sync_log": deepcopy(manager.sync_log.export()),
        "user_management": deepcopy(manager.user_management.as_dict()),
        "dirty": manager.has_unsaved_changes,
        "migration_pending": manager.project_identity_migration_pending,
    }


def test_save_as_preserves_project_identity_and_user_management(tmp_path):
    manager = DinEditorProjectManager()
    source = tmp_path / "source.json"
    target = tmp_path / "copy.json"
    manager.set_user_management(_state(manager.project_id, "Projektleiter"))
    manager.save(source)

    project_id = manager.project_id
    expected = manager.user_management.as_dict()
    manager.save(target)

    assert manager.project_id == project_id
    assert manager.path == target
    assert manager.user_management.as_dict() == expected

    reloaded = DinEditorProjectManager()
    reloaded.load(target)
    assert reloaded.project_id == project_id
    assert reloaded.user_management.as_dict() == expected


def test_recovery_restores_user_management_with_same_project_identity(tmp_path):
    manager = DinEditorProjectManager()
    path = tmp_path / "project.json"
    original = _state(manager.project_id, "Projektleiter")
    manager.set_user_management(original)
    manager.save(path)

    changed = _state(manager.project_id, "Stellvertretung")
    manager.set_user_management(changed)
    manager.save()

    recovery = recovery_path_for(path)
    assert recovery.exists()
    status = manager.recovery_status()
    assert status["available"] is True
    assert status["valid"] is True
    assert status["can_recover"] is True
    assert status["metadata"]["user_management_present"] is True

    manager.recover()
    assert manager.project_id == original.project_id
    assert manager.user_management.as_dict() == original.as_dict()
    assert manager.has_unsaved_changes is True


def test_failed_v4_load_preserves_complete_manager_state(tmp_path):
    manager = DinEditorProjectManager()
    current_path = tmp_path / "current.json"
    manager.set_user_management(_state(manager.project_id, "Bestehender Benutzer"))
    manager.save(current_path)
    before = _manager_snapshot(manager)

    broken_path = tmp_path / "broken.json"
    payload = json.loads(current_path.read_text(encoding="utf-8"))
    payload["user_management"]["project_roles"] = [
        {
            "role_assignment_id": str(uuid4()),
            "project_id": payload["project_id"],
            "user_id": str(uuid4()),
            "role_type": "deputy",
            "scope": "project",
            "valid_from": None,
            "valid_until": None,
            "assigned_by_user_id": None,
            "source_reference": "broken-reference",
            "metadata": {},
        }
    ]
    broken_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DinProjectBundleError, match="invalid ProjectOS user management data"):
        manager.load(broken_path, discard_changes=True)

    assert _manager_snapshot(manager) == before


def test_failed_v4_recovery_preserves_complete_manager_state(tmp_path):
    manager = DinEditorProjectManager()
    path = tmp_path / "project.json"
    manager.set_user_management(_state(manager.project_id, "Aktueller Benutzer"))
    manager.save(path)
    before = _manager_snapshot(manager)

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["user_management"]["project_id"] = str(uuid4())
    recovery = recovery_path_for(path)
    recovery.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DinProjectBundleError, match="recovery cannot be loaded"):
        manager.recover(discard_changes=True)

    assert _manager_snapshot(manager) == before
