"""Regression test for service identity across successful saves."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
        }
    ])
    return DinEditorProjectManager(session=session)


def test_successful_save_preserves_history_and_change_service_identity(tmp_path: Path):
    manager = _manager()
    history = manager.history
    change_service = manager.change_service
    sync_service = DinEditorSyncService(change_service)

    manager.save(tmp_path / "anlage.json")

    assert manager.history is history
    assert manager.change_service is change_service
    assert not manager.history.state()["can_undo"]

    sync_service.import_labels([{"reference": "X5", "label": "Versorgung 24V"}])

    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.history.state()["can_undo"]
    manager.change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes
