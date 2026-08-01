"""Failure-path test for discard_changes when the saved project cannot be reloaded."""
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


def test_failed_discard_reload_preserves_unsaved_manager_state(tmp_path: Path):
    manager = _manager()
    target = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Ungespeicherte Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()

    target.write_text("{not valid json", encoding="utf-8")

    try:
        manager.discard_changes()
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(target) in str(exc)
    else:
        raise AssertionError("failed discard reload was not reported")

    assert manager.path == target
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert manager.session.components[0]["label"] == "Ungespeicherte Version"
