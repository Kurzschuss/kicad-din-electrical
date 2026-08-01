"""Tests for public undo/redo availability queries."""
from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def test_change_service_uses_public_history_availability_queries():
    session = DinEditorSession(components=[{"reference": "X5", "label": "+24V SPS"}])
    history = DinEditorHistory(session)
    service = DinEditorChangeService(session, history)

    assert not history.can_undo()
    assert not history.can_redo()
    assert not service.can_undo()
    assert not service.can_redo()

    service.set_terminal_label(0, "Versorgung 24V")

    assert history.can_undo()
    assert service.can_undo()
    assert not service.can_redo()

    service.undo()

    assert history.can_redo()
    assert service.can_redo()
