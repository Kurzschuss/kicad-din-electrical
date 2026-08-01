"""Failure-path test for closing the temporary project file."""
from pathlib import Path

from . import din_editor_project_bundle
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


def test_temporary_file_close_failure_preserves_target_and_manager_state(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Neue Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()
    original_factory = din_editor_project_bundle.NamedTemporaryFile

    class FailingTemporaryFile:
        def __init__(self, *args, **kwargs):
            self._context = original_factory(*args, **kwargs)

        def __enter__(self):
            return self._context.__enter__()

        def __exit__(self, exc_type, exc, traceback):
            self._context.__exit__(exc_type, exc, traceback)
            raise OSError("simulated temporary-file close failure")

    monkeypatch.setattr(
        din_editor_project_bundle,
        "NamedTemporaryFile",
        FailingTemporaryFile,
    )

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(target) in str(exc)
    else:
        raise AssertionError("temporary-file close failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager.path == target
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))
