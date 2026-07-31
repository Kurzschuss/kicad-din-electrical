"""Tests that history keeps the original session object usable after restore."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_restore_updates_existing_session_object():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)
    history.checkpoint()
    session.components[0]["label"] = "0V"

    history.undo()

    assert history.session is session
    assert session.components == [{"reference": "X5", "label": "24V"}]
