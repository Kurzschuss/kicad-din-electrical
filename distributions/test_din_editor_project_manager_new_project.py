"""Tests for safe creation of a new DIN project."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager


def test_new_project_rejects_unsaved_changes_without_discard():
    manager = DinEditorProjectManager()
    manager.session.components.append({"reference": "X5", "label": "24V"})

    with pytest.raises(RuntimeError, match="unsaved changes"):
        manager.new_project()

    assert manager.session.components == [{"reference": "X5", "label": "24V"}]
    assert manager.has_unsaved_changes


def test_new_project_discards_state_when_explicitly_requested():
    manager = DinEditorProjectManager()
    manager.session.components.append({"reference": "X5", "label": "24V"})

    manager.new_project(discard_changes=True)

    assert manager.session.components == []
    assert manager.path is None
    assert not manager.has_unsaved_changes
