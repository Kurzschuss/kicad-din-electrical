"""Failure-path test for atomic manager updates during project saving."""
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


def test_failed_save_state_preparation_preserves_file_and_manager(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Ungespeicherte Version")

    original_path = manager.path
    original_history = manager.history
    original_change_service = manager.change_service
    original_state = manager._snapshot()
    original_history_state = manager.history.state()

    def fail_history_initialization(*args, **kwargs):
        raise RuntimeError("simulated save history initialization failure")

    monkeypatch.setattr(
        din_editor_project_manager,
        "DinEditorHistory",
        fail_history_initialization,
    )

    try:
        manager.save(target)
    except RuntimeError as exc:
        assert "save history initialization failure" in str(exc)
    else:
        raise AssertionError("save history initialization failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager.path == original_path
    assert manager.history is original_history
    assert manager.change_service is original_change_service
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history_state
    assert manager.has_unsaved_changes
    assert manager.session.components[0]["label"] == "Ungespeicherte Version"
