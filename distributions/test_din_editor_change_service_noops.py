"""Regression tests for no-op editor mutations."""
from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def _service(on_change=None):
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "terminal_label": "+24V SPS",
            "can_edit_label": True,
            "rail": 1,
            "start_te": 1,
            "end_te": 1,
            "width_te": 1,
        }
    ])
    history = DinEditorHistory(session)
    return session, history, DinEditorChangeService(session, history, on_change=on_change)


def test_same_terminal_label_is_not_recorded_as_change():
    callbacks = []
    session, history, service = _service(lambda: callbacks.append("changed"))
    before = history.capture()

    state = service.set_terminal_label(0, "  +24V SPS  ")

    assert history.capture() == before
    assert session.components[0]["label"] == "+24V SPS"
    assert not service.can_undo()
    assert not service.can_redo()
    assert callbacks == []
    assert state == session.state()


def test_same_position_is_not_recorded_as_change():
    callbacks = []
    session, history, service = _service(lambda: callbacks.append("changed"))
    before = history.capture()

    state = service.move(0, 1, 1)

    assert history.capture() == before
    assert session.components[0]["rail"] == 1
    assert session.components[0]["start_te"] == 1
    assert not service.can_undo()
    assert not service.can_redo()
    assert callbacks == []
    assert state == session.state()
