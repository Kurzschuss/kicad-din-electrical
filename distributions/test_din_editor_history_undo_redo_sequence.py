"""Tests for repeated DIN editor undo/redo transitions."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_repeated_undo_redo_restores_each_snapshot_in_order():
    session = DinEditorSession(components=[{"reference": "X5", "label": "A"}])
    history = DinEditorHistory(session)

    history.checkpoint()
    session.components[0]["label"] = "B"
    history.checkpoint()
    session.components[0]["label"] = "C"
    history.checkpoint()

    history.undo()
    assert session.components[0]["label"] == "B"
    history.undo()
    assert session.components[0]["label"] == "A"

    history.redo()
    assert session.components[0]["label"] == "B"
    history.redo()
    assert session.components[0]["label"] == "C"
