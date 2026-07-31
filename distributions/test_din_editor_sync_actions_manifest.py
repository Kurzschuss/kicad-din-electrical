"""Tests for audited KiCad manifest imports through sync actions."""
from .din_editor_sync_actions import DinEditorSyncActions
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel
from .din_editor_change_service import DinEditorChangeService
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def _actions():
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ])
    service = DinEditorSyncService(DinEditorChangeService(session))
    log = DinSyncLog()
    return DinEditorSyncActions(DinEditorSyncViewModel(service), sync_log=log), log


def test_manifest_import_records_only_changed_labels():
    actions, log = _actions()

    actions.import_manifest({
        "symbols": [
            {"reference": "X5", "label": "Versorgung 24V", "user_editable_label": True},
            {"reference": "X6", "label": "0V SPS", "user_editable_label": True},
        ]
    })

    assert len(log.entries) == 1
    assert log.entries[0]["reference"] == "X5"
    assert log.entries[0]["source"] == "KiCad"
    assert log.entries[0]["value"] == "Versorgung 24V"
    assert log.entries[0]["action"] == "imported"


def test_manifest_import_respects_overwrite_flag():
    actions, log = _actions()

    actions.import_manifest({
        "symbols": [{"reference": "X5", "label": "KiCad", "user_editable_label": True}]
    }, overwrite=False)

    assert len(log.entries) == 0
