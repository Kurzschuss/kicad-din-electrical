"""Regression tests for failed undo/redo change callbacks."""
import pytest

from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def _service_with_edit():
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
        }
    ])
    history = DinEditorHistory(session)
    service = DinEditorChangeService(session, history)
    service.set_terminal_label(0, "Versorgung 24V")
    return session, history, service


def _raising_callback():
    raise RuntimeError("change callback failed")


def test_failed_undo_callback_restores_state_and_history():
    session, history, service = _service_with_edit()
    before = history.capture()
    service.on_change = _raising_callback

    with pytest.raises(RuntimeError, match="change callback failed"):
        service.undo()

    assert history.capture() == before
    assert session.components[0]["label"] == "Versorgung 24V"
    assert service.can_undo()
    assert not service.can_redo()


def test_failed_redo_callback_restores_state_and_history():
    session, history, service = _service_with_edit()
    service.undo()
    before = history.capture()
    service.on_change = _raising_callback

    with pytest.raises(RuntimeError, match="change callback failed"):
        service.redo()

    assert history.capture() == before
    assert session.components[0]["label"] == "+24V SPS"
    assert not service.can_undo()
    assert service.can_redo()
