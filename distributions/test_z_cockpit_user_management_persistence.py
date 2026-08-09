import json
from uuid import uuid4

from .din_editor_project_bundle import export_project_bundle
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog
from .projectos_authorization import ProjectOSPermissionAssignment, ProjectOSUserProfile
from .projectos_user_management_persistence import DERIVED_NOT_PERSISTED, ProjectOSUserManagementState
from .z_cockpit_user_management_persistence import ZCockpitUserManagementPersistenceView


def test_persistence_view_marks_new_unsaved_project_as_not_yet_persisted_v4():
    manager = DinEditorProjectManager()
    state = ZCockpitUserManagementPersistenceView(manager).state()

    assert state["current_bundle_version"] == 4
    assert state["persisted_bundle_version"] is None
    assert state["bundle_v4_persisted"] is False
    assert state["migration_pending"] is False
    assert state["persisted_object_count"] == 0
    assert state["read_only"] is True


def test_persistence_view_explains_v3_migration(tmp_path):
    project_id = str(uuid4())
    path = tmp_path / "legacy-v3.json"
    path.write_text(
        json.dumps(export_project_bundle(DinEditorSession(), DinSyncLog(), project_id=project_id)),
        encoding="utf-8",
    )
    manager = DinEditorProjectManager()
    manager.load(path)

    state = ZCockpitUserManagementPersistenceView(manager).state()
    assert state["persisted_bundle_version"] == 3
    assert state["bundle_v4_persisted"] is False
    assert state["migration_pending"] is True
    assert state["migration_target_version"] == 4


def test_persistence_view_counts_v4_user_management_and_derived_data(tmp_path):
    manager = DinEditorProjectManager()
    user = ProjectOSUserProfile(display_name="Projektleiter", weight=850)
    assignment = ProjectOSPermissionAssignment(
        user_id=user.user_id,
        permission="project.read",
        source_type="direct",
        effect="allow",
    )
    manager.set_user_management(ProjectOSUserManagementState(
        project_id=manager.project_id,
        users=(user,),
        permission_assignments=(assignment,),
    ))
    path = tmp_path / "project-v4.json"
    manager.save(path)

    state = ZCockpitUserManagementPersistenceView(manager).state()
    assert state["persisted_bundle_version"] == 4
    assert state["bundle_v4_persisted"] is True
    assert state["migration_pending"] is False
    assert state["persisted_counts"]["users"] == 1
    assert state["persisted_counts"]["permission_assignments"] == 1
    assert state["persisted_object_count"] == 2
    assert state["derived_not_persisted"] == list(DERIVED_NOT_PERSISTED)
    assert state["derived_not_persisted_count"] == len(DERIVED_NOT_PERSISTED)
    assert manager.has_unsaved_changes is False
