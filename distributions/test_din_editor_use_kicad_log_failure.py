"""Failure-path test for atomic use-KiCad synchronization actions."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


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


def test_use_kicad_log_failure_rolls_back_component_history_and_dirty_state(
    monkeypatch, tmp_path: Path
):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    actions = manager.sync_actions(view_model)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])

    original_history = manager.history.state()

    def fail_record(*args, **kwargs):
        raise RuntimeError("simulated sync-log failure")

    monkeypatch.setattr(manager.sync_log, "record", fail_record)

    try:
        actions.use_kicad("X5")
    except RuntimeError as exc:
        assert "sync-log failure" in str(exc)
    else:
        raise AssertionError("sync-log failure was not reported")

    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.sync_log.entries == []
    assert manager.history.state() == original_history
    assert not manager.has_unsaved_changes
