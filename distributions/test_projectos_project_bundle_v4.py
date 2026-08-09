import json
from uuid import uuid4

import pytest

from .din_editor_project_bundle import export_project_bundle
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .projectos_authorization import ProjectOSUserProfile
from .projectos_project_bundle_v4 import (
    CURRENT_PROJECTOS_BUNDLE_VERSION,
    export_projectos_bundle,
    import_projectos_bundle_details,
)
from .projectos_user_management_persistence import ProjectOSUserManagementState


def _state(project_id: str, name: str = "Projektleiter") -> ProjectOSUserManagementState:
    return ProjectOSUserManagementState(
        project_id=project_id,
        users=(ProjectOSUserProfile(display_name=name, weight=850),),
    )


def test_bundle_v4_roundtrips_user_management():
    project_id = str(uuid4())
    state = _state(project_id)
    payload = export_projectos_bundle(
        DinEditorSession(), DinSyncLog(), project_id=project_id, user_management=state
    )

    assert payload["version"] == CURRENT_PROJECTOS_BUNDLE_VERSION
    assert payload["user_management"]["users"][0]["display_name"] == "Projektleiter"

    _, _, loaded_project_id, migration_required, loaded_state = import_projectos_bundle_details(payload)
    assert loaded_project_id == project_id
    assert migration_required is False
    assert loaded_state is not None
    assert loaded_state.as_dict() == state.as_dict()


def test_bundle_v4_rejects_foreign_user_management():
    project_id = str(uuid4())
    foreign = _state(str(uuid4()))
    with pytest.raises(Exception, match="another project"):
        export_projectos_bundle(
            DinEditorSession(), DinSyncLog(), project_id=project_id, user_management=foreign
        )


def test_manager_user_management_participates_in_dirty_state(tmp_path):
    manager = DinEditorProjectManager()
    path = tmp_path / "project.json"
    manager.save(path)
    assert manager.has_unsaved_changes is False

    manager.set_user_management(_state(manager.project_id, "Stellvertretung"))
    assert manager.has_unsaved_changes is True

    manager.save()
    assert manager.has_unsaved_changes is False
    reloaded = DinEditorProjectManager()
    reloaded.load(path)
    assert reloaded.user_management.users[0].display_name == "Stellvertretung"
    assert reloaded.has_unsaved_changes is False


def test_manager_migrates_v3_to_v4_with_empty_user_management(tmp_path):
    project_id = str(uuid4())
    legacy = export_project_bundle(DinEditorSession(), DinSyncLog(), project_id=project_id)
    assert legacy["version"] == 3
    path = tmp_path / "legacy-v3.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")

    manager = DinEditorProjectManager()
    manager.load(path)
    assert manager.project_id == project_id
    assert manager.project_identity_migration_pending is True
    assert manager.user_management.users == ()
    assert manager.has_unsaved_changes is True

    manager.save()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["version"] == 4
    assert saved["project_id"] == project_id
    assert saved["user_management"]["project_id"] == project_id
    assert manager.project_identity_migration_pending is False
    assert manager.has_unsaved_changes is False
