"""Failure-path test for creating a project target directory."""
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
        }
    ])
    return DinEditorProjectManager(session=session)


def test_target_directory_creation_failure_preserves_manager_state(monkeypatch, tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Neue Version")
    target_directory = tmp_path / "nicht-erstellbar"
    target = target_directory / "anlage-neu.json"
    original_state = manager._snapshot()
    original_history = manager.history.state()
    original_mkdir = Path.mkdir

    def fail_target_mkdir(self, *args, **kwargs):
        if self == target_directory:
            raise OSError("simulated target-directory creation failure")
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fail_target_mkdir)

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(target) in str(exc)
    else:
        raise AssertionError("target-directory creation failure was not reported")

    assert manager.path == original_path
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert original_path.exists()
    assert not target_directory.exists()
