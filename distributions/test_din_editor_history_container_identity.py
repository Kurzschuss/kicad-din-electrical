"""Tests that undo/redo preserve shared list container identity."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def test_restore_preserves_component_list_identity():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V"}])
    history = DinEditorHistory(session)
    components = session.components
    history.checkpoint()
    components[0]["label"] = "0V"

    history.undo()

    assert session.components is components
    assert components == [{"reference": "X5", "label": "24V"}]


def test_restore_preserves_sync_log_entries_identity():
    session = DinEditorSession()
    log = DinSyncLog()
    history = DinEditorHistory(session, log)
    entries = log.entries
    entries.append({"timestamp": "2026-07-31T12:00:00+00:00", "reference": "X5", "source": "KiCad", "value": "24V", "action": "imported"})
    history.checkpoint()
    entries[0]["value"] = "changed"

    history.undo()

    assert log.entries is entries
    assert entries[0]["value"] == "24V"
