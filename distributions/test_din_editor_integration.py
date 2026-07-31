"""Integration tests for the DIN editor persistence/sync workflow."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_sync_actions import DinEditorSyncActions
from .din_editor_sync_log import DinSyncLog
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager() -> DinEditorProjectManager:
    manager = DinEditorProjectManager()
    manager.session.components = [
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
    ]
    return manager


def test_project_roundtrip_and_sync_log(tmp_path: Path):
    manager = _manager()
    actions = DinEditorSyncActions(
        DinEditorSyncViewModel(DinEditorSyncService(manager and __import__("distributions.din_editor_change_service", fromlist=["DinEditorChangeService"]).DinEditorChangeService(manager.session))),
        DinSyncLog(),
    )
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    actions.use_kicad("X5")
    manager.sync_log = actions.sync_log
    path = manager.save(tmp_path / "anlage.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)
    assert loaded.session.components[0]["label"] == "Versorgung 24V"
    assert len(loaded.sync_log.entries) == 1


def test_invalid_project_is_not_saved(tmp_path: Path):
    manager = _manager()
    manager.session.components[0]["label"] = ""
    try:
        manager.save(tmp_path / "invalid.json")
    except ValueError as exc:
        assert "validation failed" in str(exc)
    else:
        raise AssertionError("invalid project was saved")
