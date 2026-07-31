"""Tests that undo/redo restores synchronization audit history."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def _entry(action):
    return {
        "timestamp": "2026-07-31T12:00:00+00:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": action,
    }


def test_undo_redo_restores_sync_log_entries():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    log = DinSyncLog()
    history = DinEditorHistory(session, log)

    history.checkpoint()
    log.entries.append(_entry("imported"))
    history.checkpoint()
    log.entries.append(_entry("updated"))

    history.undo()
    assert log.entries == [_entry("imported")]

    history.redo()
    assert log.entries == [_entry("imported"), _entry("updated")]
