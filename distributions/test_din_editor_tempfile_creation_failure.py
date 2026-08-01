"""Failure-path test for temporary-file creation during project saves."""
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


def test_temporary_file_creation_failure_preserves_target_and_manager_state(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    original_target = target.read_text(encoding="utf-8")
    manager.change_service.set_terminal_label(0, "Neue Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()

    def fail_named_temporary_file(*args, **kwargs):
        raise OSError("simulated temporary-file creation failure")

    monkeypatch.setattr(
        din_editor_project_bundle,
        "NamedTemporaryFile",
        fail_named_temporary_file,
    )

    try:
        manager.save(target)
    except DinProjectBundleError as exc:
        assert "cannot be saved" in str(exc)
        assert str(target) in str(exc)
    else:
        raise AssertionError("temporary-file creation failure was not reported")

    assert target.read_text(encoding="utf-8") == original_target
    assert manager.path == target
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))
