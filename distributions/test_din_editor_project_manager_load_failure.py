"""Tests that failed project loads preserve the current editor state."""
import pytest

from .din_editor_project_manager import DinEditorProjectManager
from .din_editor_project_bundle import save_project_bundle


def test_failed_load_preserves_current_state_and_path(tmp_path):
    manager = DinEditorProjectManager()
    target = tmp_path / "current.din.json"
    save_project_bundle(manager.session, manager.sync_log, target)
    manager.load(target)
    manager.session.components.append({"reference": "X5", "label": "24V"})
    manager.save()
    manager.session.components.append({"reference": "X6", "label": "0V"})
    bad = tmp_path / "broken.din.json"
    bad.write_text('{"version": 2, "session": [], "sync_log": []}', encoding="utf-8")

    with pytest.raises(Exception):
        manager.load(bad, discard_changes=True)

    assert manager.path == target
    assert manager.session.components == [
        {"reference": "X5", "label": "24V"},
        {"reference": "X6", "label": "0V"},
    ]
    assert manager.has_unsaved_changes
