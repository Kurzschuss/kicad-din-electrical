"""Regression test for undoable resolve-all DIN decisions."""
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
        },
        {
            "reference": "X6",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "0V SPS",
            "can_edit_label": True,
        },
    ])
    return DinEditorProjectManager(session=session)


def test_resolve_all_local_logs_are_one_undoable_operation(tmp_path: Path):
    manager = _manager()
    manager.save(tmp_path / "anlage.json")
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    actions = manager.sync_actions(view_model)

    actions.inspect([
        {"reference": "X5", "label": "Versorgung 24V"},
        {"reference": "X6", "label": "0V Versorgung"},
    ])
    actions.resolve_all("local")

    assert [component["label"] for component in manager.session.components] == [
        "+24V SPS",
        "0V SPS",
    ]
    assert len(manager.sync_log.entries) == 2
    assert {entry["action"] for entry in manager.sync_log.entries} == {"kept"}
    assert manager.history.state()["undo_depth"] == 1
    assert manager.has_unsaved_changes

    manager.change_service.undo()

    assert manager.sync_log.entries == []
    assert [component["label"] for component in manager.session.components] == [
        "+24V SPS",
        "0V SPS",
    ]
    assert not manager.has_unsaved_changes

    manager.change_service.redo()

    assert len(manager.sync_log.entries) == 2
    assert {entry["action"] for entry in manager.sync_log.entries} == {"kept"}
    assert manager.has_unsaved_changes
