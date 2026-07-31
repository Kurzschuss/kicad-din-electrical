"""Tests for protecting unsaved DIN project state during load/discard."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_project_bundle import save_project_bundle


def _manager(tmp_path):
    manager = DinEditorProjectManager()
    path = tmp_path / "project.din.json"
    save_project_bundle(manager.session, manager.sync_log, path)
    manager.load(path)
    return manager, path


def test_load_rejects_unsaved_changes_without_discard(tmp_path):
    manager, path = _manager(tmp_path)
    manager.session.components.append({"reference": "X5", "label": "24V"})

    with pytest.raises(RuntimeError, match="unsaved changes"):
        manager.load(path)

    assert manager.session.components[-1]["reference"] == "X5"
    assert manager.has_unsaved_changes


def test_load_discard_replaces_unsaved_state(tmp_path):
    manager, path = _manager(tmp_path)
    manager.session.components.append({"reference": "X5", "label": "24V"})

    manager.load(path, discard_changes=True)

    assert manager.session.components == []
    assert not manager.has_unsaved_changes


def test_discard_changes_restores_last_saved_bundle(tmp_path):
    manager, path = _manager(tmp_path)
    manager.session.components.append({"reference": "X5", "label": "24V"})

    manager.discard_changes()

    assert manager.session.components == []
    assert manager.path == path
    assert not manager.has_unsaved_changes
