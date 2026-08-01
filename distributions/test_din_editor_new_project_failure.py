"""Failure-path test for new_project initialization errors."""
from pathlib import Path

from . import din_editor_project_manager
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


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


def test_failed_new_project_preserves_current_manager_state(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Ungespeicherte Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()
    original_session = manager.session
    original_sync_log = manager.sync_log
    original_change_service = manager.change_service

    def fail_sync_log_initialization():
        raise RuntimeError("simulated new-project initialization failure")

    monkeypatch.setattr(
        din_editor_project_manager,
        "DinSyncLog",
        fail_sync_log_initialization,
    )

    try:
        manager.new_project(discard_changes=True)
    except RuntimeError as exc:
        assert "new-project initialization failure" in str(exc)
    else:
        raise AssertionError("new-project initialization failure was not reported")

    assert manager.path == original_path
    assert manager.session is original_session
    assert manager.sync_log is original_sync_log
    assert manager.change_service is original_change_service
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert manager.session.components[0]["label"] == "Ungespeicherte Version"
