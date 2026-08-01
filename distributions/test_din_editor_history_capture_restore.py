"""Tests for complete transactional history capture and restore."""
from .din_editor_history import DinEditorHistory
from .din_editor_session import DinEditorSession
from .din_editor_sync_log import DinSyncLog


def test_capture_restore_recovers_components_log_and_stacks():
    session = DinEditorSession(components=[{"reference": "X5", "label": "+24V SPS"}])
    sync_log = DinSyncLog()
    history = DinEditorHistory(session, sync_log=sync_log)

    history.checkpoint()
    session.components[0]["label"] = "Versorgung 24V"
    sync_log.record("X5", "KiCad", "Versorgung 24V", "imported")
    history.checkpoint()
    history.undo()

    captured = history.capture()
    original_state = history.state()

    session.components[0]["label"] = "Beschädigt"
    sync_log.entries.append({"reference": "X9", "action": "partial"})
    history.checkpoint()

    restored = history.restore(captured)

    assert restored == session.state()
    assert session.components[0]["label"] == "+24V SPS"
    assert sync_log.entries == []
    assert history.state() == original_state
