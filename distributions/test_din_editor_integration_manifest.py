"""Integration tests for KiCad manifest imports through the project manager."""
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_actions import DinEditorSyncActions
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager():
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ])
    manager = DinEditorProjectManager(session=session)
    service = DinEditorSyncService(manager.change_service)
    return manager, DinEditorSyncActions(DinEditorSyncViewModel(service), manager.sync_log, manager._refresh_dirty)


def test_manifest_import_updates_dirty_state_and_audit_log():
    manager, actions = _manager()

    actions.import_manifest({
        "symbols": [{"reference": "X5", "label": "Versorgung 24V", "user_editable_label": True}]
    })

    assert manager.has_unsaved_changes
    assert manager.sync_log.entries[0]["reference"] == "X5"
    assert manager.sync_log.entries[0]["value"] == "Versorgung 24V"


def test_manifest_import_undo_restores_label_and_audit_log():
    manager, actions = _manager()

    actions.import_manifest({
        "symbols": [{"reference": "X5", "label": "Versorgung 24V", "user_editable_label": True}]
    })
    assert len(manager.sync_log.entries) == 1

    manager.change_service.undo()

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.sync_log.entries == []
    assert not manager.has_unsaved_changes

    manager.change_service.redo()

    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert len(manager.sync_log.entries) == 1
    assert manager.has_unsaved_changes
