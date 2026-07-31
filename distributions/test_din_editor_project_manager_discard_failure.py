"""Tests that failed discard reloads preserve the current project state."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_project_bundle import save_project_bundle


def test_failed_discard_reload_preserves_current_state(tmp_path):
    manager = DinEditorProjectManager()
    target = tmp_path / "current.din.json"
    save_project_bundle(manager.session, manager.sync_log, target)
    manager.load(target)
    manager.session.components.append({"reference": "X5", "label": "24V"})
    manager.save(target)
    manager.session.components.append({"reference": "X6", "label": "0V"})
    bad = tmp_path / "broken.din.json"
    bad.write_text("{broken", encoding="utf-8")

    manager.path = bad
    with pytest.raises(Exception):
        manager.discard_changes()

    assert manager.path == bad
    assert manager.session.components == [
        {"reference": "X5", "label": "24V"},
        {"reference": "X6", "label": "0V"},
    ]
    assert manager.has_unsaved_changes
