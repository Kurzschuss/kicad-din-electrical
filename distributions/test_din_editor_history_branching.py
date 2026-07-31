"""Tests for DIN editor undo/redo branching semantics."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_new_checkpoint_after_undo_clears_redo_branch():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)

    history.checkpoint()
    session.components[0]["label"] = "24V DC"
    history.checkpoint()
    session.components[0]["label"] = "0V"
    history.undo()

    assert history.state()["can_redo"]
    session.components[0]["label"] = "PE"
    history.checkpoint()

    state = history.state()
    assert not state["can_redo"]
    assert state["undo_depth"] == 2


def test_duplicate_checkpoint_does_not_grow_history():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)

    history.checkpoint()
    history.checkpoint()
    history.checkpoint()

    state = history.state()
    assert state["undo_depth"] == 1
    assert not state["can_redo"]
