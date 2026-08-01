"""Failure-path test for temporary-file cleanup after a failed project save."""
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


def test_cleanup_failure_does_not_mask_atomic_replace_failure(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Neue Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()
    original_replace = Path.replace
    original_unlink = Path.unlink
    temporary_path = None

    def fail_target_replace(self, target_path):
        nonlocal temporary_path
        if Path(target_path) == target:
            temporary_path = Path(self)
            raise OSError("simulated atomic replace failure")
        return original_replace(self, target_path)

    def fail_temporary_unlink(self, *args, **kwargs):
        if temporary_path is not None and self == temporary_path:
            raise OSError("simulated temporary-file cleanup failure")
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "replace", fail_target_replace)
    monkeypatch.setattr(Path, "unlink", fail_temporary_unlink)

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(target) in str(exc)
        assert isinstance(exc.__cause__, OSError)
        assert "atomic replace failure" in str(exc.__cause__)
    else:
        raise AssertionError("atomic replace failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager.path == target
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert temporary_path is not None
    assert temporary_path.exists()

    monkeypatch.setattr(Path, "unlink", original_unlink)
    temporary_path.unlink()
