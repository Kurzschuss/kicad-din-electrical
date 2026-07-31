"""Tests that history snapshots cannot be mutated through live editor state."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def test_undo_restores_independent_component_snapshot():
    session = DinEditorSession(components=[{"reference": "X5", "label": "24V", "meta": {"kind": "terminal"}}])
    history = DinEditorHistory(session)
    history.checkpoint()

    session.components[0]["meta"]["kind"] = "changed"
    history.undo()

    assert session.components[0]["meta"] == {"kind": "terminal"}


def test_undo_restores_independent_sync_log_snapshot():
    session = DinEditorSession()
    log = DinSyncLog()
    history = DinEditorHistory(session, log)
    log.entries.append({"timestamp": "2026-07-31T12:00:00+00:00", "reference": "X5", "source": "KiCad", "value": "24V", "action": "imported"})
    history.checkpoint()

    log.entries[0]["value"] = "changed"
    history.undo()

    assert log.entries[0]["value"] == "24V"
