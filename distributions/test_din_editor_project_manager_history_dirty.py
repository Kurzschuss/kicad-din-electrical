"""Tests that undo and redo correctly update project dirty state."""
from .din_editor_project_manager import DinEditorProjectManager


def test_undo_redo_updates_dirty_state():
    manager = DinEditorProjectManager()
    manager.session.components.append({"reference": "X5", "label": "24V"})
    manager.save("project.din.json")

    manager.change_service.set_terminal_label(0, "24V DC")
    assert manager.has_unsaved_changes

    manager.change_service.undo()
    assert not manager.has_unsaved_changes

    manager.change_service.redo()
    assert manager.has_unsaved_changes
