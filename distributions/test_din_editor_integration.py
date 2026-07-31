"""Integration tests for the DIN editor persistence/sync workflow."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(components=[
        {"reference": "X5", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "+24V SPS", "can_edit_label": True},
        {"reference": "X6", "component_type": "DIN_RAIL_TERMINAL_BLOCK", "label": "0V SPS", "can_edit_label": True},
    ])
    return DinEditorProjectManager(session=session)


def _actions(manager: DinEditorProjectManager):
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    return manager.sync_actions(view_model)


def test_project_roundtrip_and_sync_log(tmp_path: Path):
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    actions.use_kicad("X5")
    path = manager.save(tmp_path / "anlage.json")

    loaded = DinEditorProjectManager()
    loaded.load(path)
    assert loaded.session.components[0]["label"] == "Versorgung 24V"
    assert loaded.session.components[0]["terminal_label"] == "Versorgung 24V"
    assert len(loaded.sync_log.entries) == 1
    assert loaded.sync_log.entries[0]["reference"] == "X5"
    assert loaded.sync_log.entries[0]["source"] == "KiCad"
    assert loaded.sync_log.entries[0]["action"] == "imported"


def test_sync_action_marks_project_dirty():
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung 24V"}])
    assert not manager.has_unsaved_changes

    actions.use_kicad("X5")
    assert manager.has_unsaved_changes
    assert len(manager.sync_log.entries) == 1


def test_sync_import_is_undoable_and_updates_dirty_state():
    manager = _manager()
    sync_service = DinEditorSyncService(manager.change_service)
    manager.save()

    sync_service.import_labels([{"reference": "X5", "label": "Versorgung 24V"}])
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes
    assert manager.history.state()["can_undo"]

    manager.change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes

    manager.change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes


def test_resolve_all_is_one_undoable_operation():
    manager = _manager()
    actions = _actions(manager)
    actions.inspect([
        {"reference": "X5", "label": "Versorgung 24V"},
        {"reference": "X6", "label": "0V Versorgung"},
    ])
    manager.save()

    actions.resolve_all("kicad")
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.session.components[1]["label"] == "0V Versorgung"
    assert len(manager.sync_log.entries) == 2
    assert manager.has_unsaved_changes

    manager.change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert manager.session.components[1]["label"] == "0V SPS"
    assert len(manager.sync_log.entries) == 0
    assert not manager.has_unsaved_changes

    manager.change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.session.components[1]["label"] == "0V Versorgung"
    assert len(manager.sync_log.entries) == 2
    assert manager.has_unsaved_changes


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


def test_undo_redo_restores_terminal_label_and_savepoint(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    change_service = manager.change_service

    change_service.set_terminal_label(0, "Versorgung 24V")
    assert manager.has_unsaved_changes
    assert manager.history.state()["can_undo"]

    change_service.undo()
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes

    change_service.redo()
    assert manager.session.components[0]["label"] == "Versorgung 24V"
    assert manager.has_unsaved_changes

    manager.save(path)
    assert not manager.history.state()["can_undo"]
    change_service = manager.change_service
    change_service.set_terminal_label(0, "Nochmals geändert")
    change_service.undo()
    assert not manager.has_unsaved_changes
    change_service.redo()
    assert manager.has_unsaved_changes


def test_load_requires_explicit_discard_when_dirty(tmp_path: Path):
    manager = _manager()
    path = manager.save(tmp_path / "anlage.json")
    manager.change_service.set_terminal_label(0, "Geändert")

    try:
        manager.load(path)
    except RuntimeError as exc:
        assert "unsaved changes" in str(exc)
    else:
        raise AssertionError("dirty project was loaded without confirmation")

    manager.load(path, discard_changes=True)
    assert manager.session.components[0]["label"] == "+24V SPS"
    assert not manager.has_unsaved_changes
