"""Regression test for undoable keep-DIN synchronization decisions."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


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


def test_keep_din_log_entry_is_undoable_and_redoable(tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    actions = manager.sync_actions(view_model)

    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    actions.keep_din("X5")

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert len(manager.sync_log.entries) == 1
    assert manager.sync_log.entries[0]["action"] == "kept"
    assert manager.history.state()["can_undo"]
    assert manager.has_unsaved_changes

    manager.change_service.undo()

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.sync_log.entries == []
    assert not manager.has_unsaved_changes

    manager.change_service.redo()

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert len(manager.sync_log.entries) == 1
    assert manager.sync_log.entries[0]["action"] == "kept"
    assert manager.has_unsaved_changes
