"""Tests for clearing DIN editor undo/redo history."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_clear_removes_undo_and_redo_entries():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)
    history.checkpoint()
    session.components[0]["label"] = "24V DC"
    history.checkpoint()
    history.undo()

    assert history.state()["can_redo"]
    history.clear()

    assert history.state() == {
        "can_undo": False,
        "can_redo": False,
        "undo_depth": 0,
        "redo_depth": 0,
    }
