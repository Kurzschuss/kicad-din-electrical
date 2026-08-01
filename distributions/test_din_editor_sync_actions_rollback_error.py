"""Regression tests for sync rollback error preservation."""
import pytest

from .din_editor_sync_actions import DinEditorSyncActions


class _History:
    def __init__(self):
        self.restored = None

    def restore(self, captured):
        self.restored = captured


def test_rollback_callback_failure_does_not_mask_operation_error():
    actions = DinEditorSyncActions.__new__(DinEditorSyncActions)
    actions.on_change = lambda: (_ for _ in ()).throw(RuntimeError("refresh failed"))
    history = _History()
    captured = {"current": {"components": []}, "undo": [], "redo": []}

    with pytest.raises(ValueError, match="sync failed"):
        try:
            raise ValueError("sync failed")
        except Exception:
            actions._rollback_history(history, captured)
            raise

    assert history.restored is captured
