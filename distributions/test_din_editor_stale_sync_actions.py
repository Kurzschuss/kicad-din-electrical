"""Tests for synchronization actions after a project-state replacement."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def test_actions_created_before_new_project_are_rejected():
    manager = DinEditorProjectManager(
        session=DinEditorSession(components=[
            {
                "reference": "X5",
                "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                "label": "+24V SPS",
                "can_edit_label": True,
            }
        ])
    )
    old_session = manager.session
    old_sync_log = manager.sync_log
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    actions = manager.sync_actions(view_model)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])

    manager.new_project(discard_changes=True)

    with pytest.raises(RuntimeError, match="no longer bound to the active project"):
        actions.use_kicad("X5")

    assert old_session.components[0]["label"] == "+24V SPS"
    assert old_sync_log.entries == []
    assert manager.session.components == []
    assert manager.sync_log.entries == []
    assert not manager.has_unsaved_changes
