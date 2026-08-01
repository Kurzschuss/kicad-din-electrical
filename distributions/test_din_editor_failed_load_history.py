"""Failure-path test for atomic manager replacement during project loading."""
from pathlib import Path

from . import din_editor_project_manager
from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession


def _manager(label: str) -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": label,
            "can_edit_label": True,
        }
    ])
    return DinEditorProjectManager(session=session)


def test_failed_history_setup_during_load_preserves_current_manager_state(
    monkeypatch, tmp_path: Path
):
    manager = _manager("Aktives Projekt")
    original_path = manager.save(tmp_path / "aktiv.json")
    manager.change_service.set_terminal_label(0, "Ungespeicherte Version")

    replacement = _manager("Neues Projekt")
    replacement_path = replacement.save(tmp_path / "neu.json")

    original_session = manager.session
    original_sync_log = manager.sync_log
    original_history = manager.history
    original_change_service = manager.change_service
    original_state = manager._snapshot()
    original_history_state = manager.history.state()

    def fail_history_initialization(*args, **kwargs):
        raise RuntimeError("simulated load history initialization failure")

    monkeypatch.setattr(
        din_editor_project_manager,
        "DinEditorHistory",
        fail_history_initialization,
    )

    try:
        manager.load(replacement_path, discard_changes=True)
    except RuntimeError as exc:
        assert "load history initialization failure" in str(exc)
    else:
        raise AssertionError("load history initialization failure was not reported")

    assert manager.path == original_path
    assert manager.session is original_session
    assert manager.sync_log is original_sync_log
    assert manager.history is original_history
    assert manager.change_service is original_change_service
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history_state
    assert manager.has_unsaved_changes
    assert manager.session.components[0]["label"] == "Ungespeicherte Version"
