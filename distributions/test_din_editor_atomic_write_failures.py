"""Failure-path tests for atomic DIN project persistence."""
import os
from pathlib import Path

from .din_editor_project_bundle import DinProjectBundleError, save_project_bundle
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


def test_temporary_file_fsync_failure_preserves_existing_target(monkeypatch, tmp_path: Path):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Neue Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()

    def fail_fsync(file_descriptor: int) -> None:
        raise OSError("simulated fsync failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)

    try:
        save_project_bundle(manager.session, manager.sync_log, target)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(target) in str(exc)
    else:
        raise AssertionError("fsync failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))
