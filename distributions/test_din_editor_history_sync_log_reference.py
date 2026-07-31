"""Tests that history keeps the original sync log object usable after restore."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def test_restore_updates_existing_sync_log_object():
    session = DinEditorSession()
    log = DinSyncLog()
    history = DinEditorHistory(session, log)
    log.entries.append({
        "timestamp": "2026-07-31T12:00:00+00:00",
        "reference": "X5",
        "source": "KiCad",
        "value": "24V",
        "action": "imported",
    })
    history.checkpoint()
    log.entries[0]["value"] = "changed"

    history.undo()

    assert history.sync_log is log
    assert log.entries[0]["value"] == "24V"
