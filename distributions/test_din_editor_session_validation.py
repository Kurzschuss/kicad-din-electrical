"""Tests for DIN editor session configuration validation."""
import pytest

from .din_editor_session import DinEditorSession


@pytest.mark.parametrize("rails,te_per_rail", [(0, 12), (-1, 12), (18, 0), (18, -1)])
def test_session_rejects_non_positive_layout_configuration(rails, te_per_rail):
    with pytest.raises(ValueError):
        DinEditorSession(rails=rails, te_per_rail=te_per_rail)


def test_session_accepts_positive_layout_configuration():
    session = DinEditorSession(rails=2, te_per_rail=6)
    assert session.rails == 2
    assert session.te_per_rail == 6
