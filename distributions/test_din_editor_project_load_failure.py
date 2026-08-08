"""Regressionstests für transaktionssicheres Laden von DIN-Projekten."""
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
        },
        {
            "reference": "X6",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "0V SPS",
            "can_edit_label": True,
        },
    ])
    return DinEditorProjectManager(session=session)


def test_corrupt_load_preserves_current_manager_state(tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")

    manager.change_service.set_terminal_label(0, "Geändert")
    assert manager.has_unsaved_changes

    original_state = manager._snapshot()
    original_saved_state = manager._saved_state.copy()
    original_history = manager.history.state()
    original_session = manager.session
    original_sync_log = manager.sync_log
    original_change_service = manager.change_service

    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text('{"version": 2, "session":', encoding="utf-8")

    try:
        manager.load(corrupt_path, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(corrupt_path) in str(exc)
    else:
        raise AssertionError("corrupt project loaded without an error")

    assert manager.path == original_path
    assert manager._snapshot() == original_state
    assert manager._saved_state == original_saved_state
    assert manager.history.state() == original_history
    assert manager.session is original_session
    assert manager.sync_log is original_sync_log
    assert manager.change_service is original_change_service
    assert manager.has_unsaved_changes
