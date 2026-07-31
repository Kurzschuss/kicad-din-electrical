"""Integration tests for the DIN editor persistence/sync workflow."""
from pathlib import Path

from .din_editor_change_service import DinEditorChangeService
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


def _actions(manager: DinEditorProjectManager) -> DinEditorSyncActions:
    change_service = DinEditorChangeService(manager.session)
    view_model = DinEditorSyncViewModel(DinEditorSyncService(change_service))
    return DinEditorSyncActions(view_model, DinSyncLog())


def test_project_roundtrip_and_sync_log(tmp_path: Path):
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    actions.use_kicad("X5")
    manager.sync_log = actions.sync_log
    path = manager.save(tmp_path / "anlage.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)
    assert loaded.session.components[0]["label"] == "Versorgung 24V"
    assert loaded.session.components[0]["terminal_label"] == "Versorgung 24V"
    assert len(loaded.sync_log.entries) == 1
    assert loaded.sync_log.entries[0]["reference"] == "X5"
    assert loaded.sync_log.entries[0]["source"] == "KiCad"
    assert loaded.sync_log.entries[0]["action"] == "imported"


def test_invalid_project_is_not_saved(tmp_path: Path):
    manager = _manager()
    manager.session.components[0]["label"] = ""
    path = tmp_path / "invalid.json"

    try:
        manager.save(path)
    except ValueError as exc:
        assert "validation failed" in str(exc)
    else:
        raise AssertionError("invalid project was saved")

    assert not path.exists()


def test_undo_redo_restores_terminal_label():
    manager = _manager()
    change_service = DinEditorChangeService(manager.session)

    change_service.set_terminal_label(0, "Versorgung 24V")
    assert manager.session.components[0]["label"] == "Versorgung 24V"

    change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"

    change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
