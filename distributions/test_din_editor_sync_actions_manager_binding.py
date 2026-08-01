"""Tests for project-manager binding of synchronization actions."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager(label: str) -> DinEditorProjectManager:
    return DinEditorProjectManager(
        session=DinEditorSession(components=[
            {
                "reference": "X5",
                "component_type": "DIN_RAIL_TERMINAL_BLOCK",
                "label": label,
                "can_edit_label": True,
            }
        ])
    )


def test_sync_actions_rejects_view_model_from_another_manager():
    manager = _manager("+24V SPS")
    other = _manager("0V SPS")
    foreign_view_model = DinEditorSyncViewModel(DinEditorSyncService(other.change_service))

    with pytest.raises(ValueError, match="not bound to this project manager"):
        manager.sync_actions(foreign_view_model)

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert other.session.components[0]["label"] == "0V SPS"
    assert manager.sync_log.entries == []
    assert other.sync_log.entries == []
    assert not manager.has_unsaved_changes
    assert not other.has_unsaved_changes


def test_sync_actions_accepts_matching_view_model():
    manager = _manager("+24V SPS")
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))

    actions = manager.sync_actions(view_model)

    assert actions.view_model is view_model
    assert actions.sync_log is manager.sync_log
