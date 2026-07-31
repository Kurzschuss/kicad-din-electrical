"""Tests for no-op behavior at the ends of the DIN editor history."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_undo_without_history_does_not_create_redo_entry():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)

    before = session.state()
    result = history.undo()

    assert result == before
    assert history.state() == {
        "can_undo": False,
        "can_redo": False,
        "undo_depth": 0,
        "redo_depth": 0,
    }


def test_redo_without_history_does_not_create_undo_entry():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)

    before = session.state()
    result = history.redo()

    assert result == before
    assert history.state() == {
        "can_undo": False,
        "can_redo": False,
        "undo_depth": 0,
        "redo_depth": 0,
    }
