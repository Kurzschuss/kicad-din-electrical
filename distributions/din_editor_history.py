"""Undo/redo support for the complete DIN editor state."""
from copy import deepcopy

from .din_editor_session import DinEditorSession


class DinEditorHistory:
    def __init__(self, session: DinEditorSession, sync_log=None):
        self.session = session
        self.sync_log = sync_log
        self._undo = []
        self._redo = []

    def _snapshot(self):
        state = {"components": deepcopy(self.session.components)}
        if self.sync_log is not None:
            state["sync_log"] = deepcopy(self.sync_log.entries)
        return state

    def _restore(self, state: dict) -> dict:
        self.session.components[:] = deepcopy(state["components"])
        if self.sync_log is not None:
            self.sync_log.entries[:] = deepcopy(state.get("sync_log", []))
        return self.session.state()

    def capture(self) -> dict:
        """Capture the complete mutable history state for transactional rollback."""
        return {
            "current": self._snapshot(),
            "undo": deepcopy(self._undo),
            "redo": deepcopy(self._redo),
        }

    def restore(self, captured: dict) -> dict:
        """Restore a state previously returned by :meth:`capture`."""
        state = self._restore(captured["current"])
        self._undo = deepcopy(captured["undo"])
        self._redo = deepcopy(captured["redo"])
        return state

    def checkpoint(self):
        """Record the state immediately before the next mutation."""
        snapshot = self._snapshot()
        if self._undo and self._undo[-1] == snapshot:
            return
        self._undo.append(snapshot)
        self._redo.clear()

    def undo(self) -> dict:
        if not self._undo:
            return self.session.state()

        current = self._snapshot()
        target = self._undo.pop()
        self._redo.append(current)

        # If the current state is itself a checkpoint, that checkpoint is
        # the state after the last mutation; undo must move to its predecessor.
        if current == target and self._undo:
            target = self._undo[-1]

        return self._restore(target)

    def redo(self) -> dict:
        if not self._redo:
            return self.session.state()
        current = self._snapshot()
        target = self._redo.pop()
        self._undo.append(current)
        return self._restore(target)

    def can_undo(self) -> bool:
        """Return whether an undo step is currently available."""
        return bool(self._undo)

    def can_redo(self) -> bool:
        """Return whether a redo step is currently available."""
        return bool(self._redo)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def state(self) -> dict:
        return {
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "undo_depth": len(self._undo),
            "redo_depth": len(self._redo),
        }
