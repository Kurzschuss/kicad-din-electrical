"""Regression tests for failed editor mutations."""
import pytest

from .din_editor_change_service import DinEditorChangeService
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession


def _service() -> tuple[DinEditorSession, DinEditorHistory, DinEditorChangeService]:
    session = DinEditorSession(components=[
        {
            "reference": "X5",
            "component_type": "DIN_RAIL_TERMINAL_BLOCK",
            "label": "+24V SPS",
            "can_edit_label": True,
            "rail": 0,
            "start_te": 0,
        }
    ])
    history = DinEditorHistory(session)
    return session, history, DinEditorChangeService(session, history)


@pytest.mark.parametrize(
    "operation",
    [
        lambda service: service.set_terminal_label(99, "Versorgung 24V"),
        lambda service: service.move(99, 1, 4),
    ],
)
def test_failed_mutation_restores_state_and_history(operation):
    session, history, service = _service()
    before = history.capture()

    with pytest.raises(IndexError):
        operation(service)

    assert history.capture() == before
    assert session.components[0]["label"] == "+24V SPS"
    assert session.components[0]["rail"] == 0
    assert session.components[0]["start_te"] == 0
    assert not service.can_undo()
    assert not service.can_redo()
