"""Failure-path test for loading an invalid project with discard enabled."""
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


def test_failed_load_with_discard_preserves_current_manager_state(tmp_path: Path):
    manager = _manager()
    original_path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Ungespeicherte Version")
    original_state = manager._snapshot()
    original_history = manager.history.state()
    invalid_project = tmp_path / "defekt.json"
    invalid_project.write_text("{not valid json", encoding="utf-8")

    try:
        manager.load(invalid_project, discard_changes=True)
    except DinProjectBundleError as exc:
        assert "invalid JSON" in str(exc)
        assert str(invalid_project) in str(exc)
    else:
        raise AssertionError("invalid project load was not reported")

    assert manager.path == original_path
    assert manager._snapshot() == original_state
    assert manager.history.state() == original_history
    assert manager.has_unsaved_changes
    assert manager.session.components[0]["label"] == "Ungespeicherte Version"
