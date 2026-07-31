"""Integration tests for KiCad manifest imports through the sync service."""
from .din_editor_change_service import DinEditorChangeService
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService


def _service():
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ])
    return DinEditorSyncService(DinEditorChangeService(session))


def test_manifest_import_is_undoable():
    service = _service()
    manifest = {"symbols": [{"reference": "X5", "label": "Versorgung 24V", "user_editable_label": True}]}

    service.import_manifest_labels(manifest)
    assert service.session.components[0]["label"] == "Versorgung 24V"
    assert service.change_service.can_undo()

    service.change_service.undo()
    assert service.session.components[0]["label"] == "+24V SPS"


def test_noop_manifest_import_does_not_create_history_entry():
    service = _service()
    manifest = {"symbols": [{"reference": "X5", "label": "+24V SPS", "user_editable_label": True}]}

    service.import_manifest_labels(manifest)

    assert not service.change_service.can_undo()
