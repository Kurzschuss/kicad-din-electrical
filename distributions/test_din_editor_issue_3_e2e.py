"""End-to-end regression for the DIN editor workflow from issue #3."""
from pathlib import Path

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_session import DinEditorSession
from .din_editor_sync_service import DinEditorSyncService
from .din_editor_sync_view_model import DinEditorSyncViewModel


def _manager() -> DinEditorProjectManager:
    session = DinEditorSession(
        components=[
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
        ]
    )
    return DinEditorProjectManager(session=session)


def _actions(manager: DinEditorProjectManager):
    view_model = DinEditorSyncViewModel(DinEditorSyncService(manager.change_service))
    return manager.sync_actions(view_model)


def test_save_sync_save_as_reload_then_undo_redo(tmp_path: Path):
    """Exercise the complete issue #3 workflow without persisting stale history."""
    manager = _manager()
    original_path = tmp_path / "anlage.json"
    save_as_path = tmp_path / "anlage-kicad.json"

    # 1. Project change -> 2. Save.
    manager.change_service.set_terminal_label(0, "Versorgung DIN")
    assert manager.has_unsaved_changes
    manager.save(original_path)
    assert manager.path == original_path
    assert not manager.has_unsaved_changes
    assert not manager.history.state()["can_undo"]

    project_id = manager.project_id

    # 3. KiCad sync. A conflicting terminal label is explicitly accepted.
    actions = _actions(manager)
    actions.inspect([{"reference": "X5", "label": "Versorgung KiCad"}])
    actions.use_kicad("X5")

    assert manager.session.components[0]["label"] == "Versorgung KiCad"
    assert manager.session.components[0]["terminal_label"] == "Versorgung KiCad"
    assert manager.has_unsaved_changes
    assert len(manager.sync_log.entries) == 1
    assert manager.sync_log.entries[0]["reference"] == "X5"
    assert manager.sync_log.entries[0]["source"] == "KiCad"
    assert manager.sync_log.entries[0]["action"] == "imported"

    # 4. Save-As must preserve the original file and make the target current.
    manager.save(save_as_path)
    assert manager.path == save_as_path
    assert not manager.has_unsaved_changes
    assert original_path.exists()
    assert save_as_path.exists()

    original = DinEditorProjectManager()
    original.load(original_path)
    assert original.session.components[0]["label"] == "Versorgung DIN"
    assert original.sync_log.entries == []

    # 5. Reload the Save-As target and verify persisted project/sync state.
    reloaded = DinEditorProjectManager()
    reloaded.load(save_as_path)
    assert reloaded.path == save_as_path
    assert reloaded.project_id == project_id
    assert reloaded.session.components[0]["label"] == "Versorgung KiCad"
    assert reloaded.session.components[0]["terminal_label"] == "Versorgung KiCad"
    assert len(reloaded.sync_log.entries) == 1
    assert reloaded.sync_log.entries[0]["reference"] == "X5"
    assert reloaded.sync_log.entries[0]["source"] == "KiCad"
    assert reloaded.sync_log.entries[0]["action"] == "imported"
    assert not reloaded.has_unsaved_changes
    assert not reloaded.history.state()["can_undo"]
    assert not reloaded.history.state()["can_redo"]

    # 6. Undo/Redo after reload starts from the persisted state and remains
    # deterministic. Pre-save history is intentionally not serialized.
    reloaded.change_service.set_terminal_label(0, "Nach Reload")
    assert reloaded.session.components[0]["label"] == "Nach Reload"
    assert reloaded.has_unsaved_changes
    assert reloaded.history.state()["can_undo"]

    reloaded.change_service.undo()
    assert reloaded.session.components[0]["label"] == "Versorgung KiCad"
    assert reloaded.session.components[0]["terminal_label"] == "Versorgung KiCad"
    assert not reloaded.has_unsaved_changes
    assert reloaded.history.state()["can_redo"]

    reloaded.change_service.redo()
    assert reloaded.session.components[0]["label"] == "Nach Reload"
    assert reloaded.session.components[0]["terminal_label"] == "Nach Reload"
    assert reloaded.has_unsaved_changes
    assert reloaded.history.state()["can_undo"]
